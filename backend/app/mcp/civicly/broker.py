"""Separated official/domain namespaces; no raw transport capability in public tools."""
import asyncio,json,time
from contextlib import asynccontextmanager
from uuid import uuid4
from mcp import Client
from app.mcp.runtime import CITY_GRAPH
from app.graph.schema import Registry,utc_now
from app.graph.models import NodeRecord,EdgeRecord
from app.graph.analysis.models import ProofPath
from app.mcp.broker import BrokerError,error_code,open_broker as open_official
from .contracts import READ,SERVER,VERSION,INVENTORY_HASH,Context,context,input_schema,validate,bounded,digest
from .models import TraceRecord
from .storage import TraceStore
from .runtime import parameters,connections


def validate_result(name,value,c):
    validate(READ[name]['output_schema'],value)
    if value['context']!=c.model_dump(mode='json') or value['execution_id']!=c.execution_id or value['trace_id']!=c.trace_id or value['server_id']!=SERVER or value['tool_name']!=name or value['inventory_version']!=INVENTORY_HASH:raise ValueError('Result identity mismatch')
    registry=Registry();nodes={}
    for row in value['data']['nodes']:
        n=NodeRecord.model_validate_json(json.dumps(row));registry.validate_node(n.kind,n.properties)
        if n.id!=n.properties['id'] or set(n.labels)!=set(registry.labels(n.kind))-{registry.base_label}:raise ValueError('Node identity/labels')
        if n.id in nodes:raise ValueError('Duplicate node')
        nodes[n.id]=n
    edges={}
    for row in value['data']['edges']:
        e=EdgeRecord.model_validate_json(json.dumps(row));s,t=nodes[e.source],nodes[e.target]
        registry.validate_edge(e.kind,s.kind,s.properties,t.kind,t.properties,e.properties)
        if e.id!=e.properties['id'] or e.id in edges:raise ValueError('Edge identity')
        edges[e.id]=e
    seen_paths=set()
    for path in value['data']['paths']:
        p=ProofPath.model_validate_json(json.dumps(path))
        if p.id in seen_paths:raise ValueError('Duplicate proof path')
        seen_paths.add(p.id)
        ids=path['node_ids'];rels=path['edge_ids'];directions=path['directions']
        if len(ids)!=len(rels)+1 or len(rels)>6 or len(directions)!=len(rels):raise ValueError('Path budget/shape')
        for i,id in enumerate(rels):
            e=edges[id]
            if directions[i] not in {'OUTGOING','INCOMING'}:raise ValueError('Invalid path direction')
            ends=(e.source,e.target) if directions[i]=='OUTGOING' else (e.target,e.source)
            if ends!=(ids[i],ids[i+1]):raise ValueError('Path endpoints/direction')
    ev={n.id for n in nodes.values() if n.kind=='Evidence'}
    if not set(value['source_evidence_ids'])<=ev:raise ValueError('Missing evidence context')
    if value['status'] in {'ERROR','UNAVAILABLE','PERMISSION_DENIED'} and value['error'] is None:raise ValueError('Missing explicit error')
    return value


class DomainBroker:
    def __init__(self,client,store,*,timeout=8,max_calls=32,source_graph=CITY_GRAPH):
        if not .01<=timeout<=10 or not 1<=max_calls<=64:raise ValueError('Finite broker budgets required')
        from app.active import require_source
        self.source_graph=require_source(source_graph)
        self.__client=client;self.__store=store;self.timeout=timeout;self.max_calls=max_calls;self.calls=0;self.broken=False;self.lock=asyncio.Lock()
    async def discover(self):
        info=self.__client.server_info
        if info.name!=SERVER or info.version!=VERSION:raise BrokerError('SERVER_IDENTITY_MISMATCH')
        async with asyncio.timeout(self.timeout):listing=await self.__client.list_tools()
        if listing.next_cursor is not None or len(listing.tools)!=len(READ) or {t.name for t in listing.tools}!=set(READ):raise BrokerError('INVENTORY_MISMATCH')
        for t in listing.tools:
            if digest(t.input_schema)!=digest(input_schema(t.name,True)) or digest(t.output_schema)!=digest(READ[t.name]['output_schema']):raise BrokerError('TOOL_SCHEMA_MISMATCH')
        self.protocol=self.__client.protocol_version
        self.operator_initialization={'server':info.model_dump(mode='json'),'protocol_version':self.protocol}
        self.operator_inventory=[t.model_dump(mode='json') for t in listing.tools]
    def tools(self):return [{'name':'civicly::'+name,'description':t['description'],'input_schema':input_schema(name),'output_schema':t['output_schema']} for name,t in sorted(READ.items())]
    async def call(self,qualified_name,args,*,invocation=None,rationale_summary=None):
        c=invocation or context(args.get('investigation_id') if isinstance(args,dict) else None).model_copy(update={'source_graph':self.source_graph})
        if not isinstance(c,Context) or c.source_graph!=self.source_graph:raise BrokerError('INVALID_CONTEXT')
        started,clock=utc_now(),time.perf_counter();result=None;code='SUCCESS'
        name=qualified_name.removeprefix('civicly::') if isinstance(qualified_name,str) else ''
        try:
            if not isinstance(qualified_name,str) or not qualified_name.startswith('civicly::') or name not in READ:raise BrokerError('DENIED_TOOL')
            if self.broken:raise BrokerError('SESSION_UNAVAILABLE')
            if self.calls>=self.max_calls:raise BrokerError('CALL_BUDGET')
            try:bounded(args);validate(input_schema(name),args)
            except Exception:raise BrokerError('INVALID_ARGUMENTS') from None
            async with self.lock:
                if self.calls>=self.max_calls:raise BrokerError('CALL_BUDGET')
                self.calls+=1
                async with asyncio.timeout(self.timeout):
                    wire=await self.__client.call_tool(name,{**args,'_context':c.model_dump(mode='json')},read_timeout_seconds=self.timeout)
                if wire.is_error:raise BrokerError('REMOTE_TOOL_ERROR')
                if len(wire.content)!=1 or wire.content[0].type!='text' or len(wire.content[0].text.encode())>524288:raise BrokerError('INVALID_OUTPUT')
                result=json.loads(wire.content[0].text)
                if wire.structured_content!=result:raise BrokerError('INVALID_OUTPUT')
                try:validate_result(name,result,c)
                except Exception:raise BrokerError('INVALID_OUTPUT') from None
                saved=await asyncio.to_thread(self.__store.get,c.execution_id)
                if saved is None or saved.output_sha256!=digest(result):raise BrokerError('TRACE_NOT_PERSISTED')
            return result
        except Exception as exc:
            code=error_code(exc)
            if code in {'TIMEOUT','TRANSPORT_FAILURE','INVALID_OUTPUT','TRACE_NOT_PERSISTED'}:self.broken=True
            raise BrokerError(code) from None
        finally:
            # Distinct host observation, parented to requested server execution; never
            # overwrite a server success when output was corrupted after transport.
            child=c.model_copy(update={'execution_id':uuid4().hex,'parent_execution_id':c.execution_id})
            try:arg_hash=digest(args)
            except Exception:arg_hash=digest({'withheld':True})
            record=TraceRecord(context=child,rationale_summary=rationale_summary,phase='BROKER',server_id=SERVER,server_version=VERSION,
                tool_name=name if name in READ else 'UNAUTHORIZED_TOOL',inventory_version=INVENTORY_HASH,
                schema_sha256=digest(input_schema(name)) if name in READ else digest({}),arguments_sha256=arg_hash,
                started_at=started,finished_at=utc_now(),latency_ms=(time.perf_counter()-clock)*1000,status=code,
                error_code=None if code=='SUCCESS' else code,protocol_version=getattr(self,'protocol',None),
                validated_output=code=='SUCCESS',output_sha256=digest(result) if result and code=='SUCCESS' else None,
                graph_revision=result['graph_revision'] if result and code=='SUCCESS' else None,
                source_evidence_ids=result['source_evidence_ids'] if result and code=='SUCCESS' else [],
                graph_path_ids=[p['id'] for p in result['data']['paths']] if result and code=='SUCCESS' else [])
            try:await asyncio.to_thread(self.__store.append,record)
            except Exception:raise BrokerError('TRACE_PERSISTENCE_FAILED') from None


@asynccontextmanager
async def open_domain(*,timeout=8,max_calls=32):
    try:
        with connections() as (_,writer,name),parameters() as params:
            store=TraceStore(writer,name)
            async with Client(params,mode='legacy',read_timeout_seconds=timeout) as client:
                broker=DomainBroker(client,store,timeout=timeout,max_calls=max_calls);await broker.discover();yield broker
    except BrokerError:raise
    except Exception as exc:raise BrokerError(error_code(exc)) from None
