"""Trusted shared-graph bootstrap. Model sees only the combined safe catalog."""
import asyncio,json,tempfile,time,copy
from contextlib import asynccontextmanager
from mcp import Client,StdioServerParameters
from .isolation import agent_files
from app.active import active_scope,load,require_source
from app.mcp.runtime import ROOT,RuntimeCredentials
from app.mcp.broker import open_broker
from app.mcp.civicly.broker import DomainBroker
from app.mcp.civicly.runtime import connections
from app.mcp.civicly.storage import TraceStore
from app.mcp.civicly.contracts import Context,digest
from app.mcp.policy import Request

@asynccontextmanager
async def brokers(profile,path,*,timeout=8,memory_path=None):
    with active_scope(profile),agent_files(),connections() as (_,writer,name),tempfile.TemporaryDirectory(prefix='civicly-b10-domain-') as cwd:
        params=StdioServerParameters(command=str(ROOT/'backend/.venv/bin/python'),args=['-m','app.agents.server',str(path)]+([str(memory_path)] if memory_path is not None else []),
            cwd=cwd,env={'PYTHONPATH':str(ROOT/'backend'),'PYTHONUNBUFFERED':'1'})
        creds=RuntimeCredentials(username=profile.read_user,password=profile.read_password,graph=profile.graph)
        traces=[];store=TraceStore(writer,name)
        async with open_broker(traces,timeout=min(timeout,10),max_calls=64,source_graph=profile.graph,credentials=creds) as official:
            async with Client(params,mode='legacy',read_timeout_seconds=timeout) as client:
                domain=DomainBroker(client,store,timeout=timeout,max_calls=64,source_graph=profile.graph)
                await domain.discover()
                yield Tools(official,domain,store,traces,profile.graph)

class Tools:
    def __init__(self,official,domain,store,traces,graph):
        self.official,self.domain,self.store,self.traces,self.graph=official,domain,store,traces,graph
        self._catalog=None;self._reads={};self._read_revision=None;self.last_cache_receipt=None
        self._legacy_catalog=None
    def catalog(self):
        if self._catalog is not None:return copy.deepcopy(self._catalog)
        # No raw vendor query/graph selectors. Actual discovered schemas verified by brokers.
        schema=Request.model_json_schema();schema['properties'].pop('graph',None);schema['properties'].pop('tool',None);schema['required']=[k for k in schema.get('required',[]) if k not in {'tool','graph'}]
        rows=[];legacy=[]
        descriptions={t['name']:t.get('description','') for t in self.official.operator_inventory}
        for tool in self.official.tools():
            name=tool['name'];shape=copy.deepcopy(schema)
            legacy.append({'name':'official::'+name,'description':'Approved fixed templates only; '+descriptions[name],'input_schema':copy.deepcopy(schema)})
            fields={'query_graph_readonly':{'template','id','as_of'},'get_graph_schema':set(),'get_node_schema':{'label','sample_size'},'get_relationship_schema':{'relationship_type','sample_size'}}[name]
            shape['properties']={k:v for k,v in shape['properties'].items() if k in fields}
            shape['required']={'query_graph_readonly':['template','id'],'get_graph_schema':[],'get_node_schema':['label'],'get_relationship_schema':['relationship_type']}[name]
            detail=' query_graph_readonly requires template="node" and id for a current node lookup (omit as_of), or template="drainage_edges", id and as_of for outgoing drainage facts.' if name=='query_graph_readonly' else ''
            rows.append({'name':'official::'+name,'description':'Approved fixed templates only; '+descriptions[name]+detail,'input_schema':shape})
        domain=[{k:t[k] for k in ['name','description','input_schema']} for t in self.domain.tools()]
        self._legacy_catalog=legacy+domain
        self._catalog=rows+domain
        return copy.deepcopy(self._catalog)
    def bind_inventory(self,expected_hash):
        """Recognize the exact prior catalog; never rewrite a checkpoint hash."""
        if digest(self.catalog())==expected_hash:return
        if self._legacy_catalog is not None and digest(self._legacy_catalog)==expected_hash:
            self._catalog=copy.deepcopy(self._legacy_catalog);return
        raise ValueError('CHECKPOINT_INVENTORY_NOT_SUPPORTED')
    @property
    def inventory_hash(self):return digest(self.catalog())
    def bind_read_cache(self,revision_reader):
        self._read_revision=revision_reader
    async def call(self,name,args,ctx,summary,*,cutoff=None):
        self.last_cache_receipt=None
        # Organizational sources have a separate revision/revocation lifecycle.
        # Do not reuse a cached source-graph-only key for those reads.
        revision=self._read_revision() if self._read_revision is not None and name not in {'civicly::get_organizational_procedures','civicly::get_source_document_excerpt'} else None
        scope={k:v for k,v in ctx.model_dump(mode='json').items() if k not in {'execution_id','parent_execution_id'}}
        key=digest({'name':name,'args':args,'scope':scope,'cutoff':cutoff,'inventory':self.inventory_hash,'graph':self.graph,'revision':revision})
        if revision is not None and key in self._reads:
            saved=self._reads[key]
            if self._read_revision()==revision:
                self.last_cache_receipt={'kind':'CACHED_READ_REFERENCE','original_execution_id':saved['execution'],'graph_revision':revision,'scope_sha256':digest(scope),'bounded_negative_is_not_absence':True}
                return copy.deepcopy(saved['value'])
        result=await self._actual_call(name,args,ctx,summary,cutoff=cutoff)
        if revision is not None and self._read_revision()==revision and result.get('status','SUCCESS') not in {'ERROR','PERMISSION_DENIED'}:
            self._reads={k:v for k,v in self._reads.items() if v['revision']==revision}
            if len(self._reads)>=32:self._reads.pop(next(iter(self._reads)))
            self._reads[key]={'value':copy.deepcopy(result),'execution':result.get('execution_id',ctx.execution_id),'revision':revision}
        return result
    async def _actual_call(self,name,args,ctx,summary,*,cutoff=None):
        if not isinstance(args,dict) or any(k in args for k in ['graph','graphName','query','_context','tool']):raise ValueError('Scope/query selectors denied')
        if cutoff is not None:
            from app.graph.schema import timestamp
            if args.get('as_of') is not None and timestamp(args['as_of'])>timestamp(cutoff):raise ValueError('Future knowledge cutoff denied')
            schema=next((t['input_schema'] for t in self.catalog() if t['name']==name),{})
            if (name.startswith('civicly::') and 'as_of' in schema.get('properties',{})) or (name=='official::query_graph_readonly' and args.get('template')=='drainage_edges'):
                args={**args,'as_of':args.get('as_of',cutoff)}
        if name.startswith('civicly::'):
            return await self.domain.call(name,args,invocation=ctx,rationale_summary=summary)
        if name not in {t['name'] for t in self.catalog() if t['name'].startswith('official::')}:raise ValueError('Unapproved tool')
        from app.graph.schema import utc_now
        from app.mcp.civicly.models import TraceRecord
        from app.mcp.broker import error_code
        started,clock=utc_now(),time.perf_counter();result=None;code='SUCCESS'
        try:
            result=await self.official.call({**args,'tool':name.removeprefix('official::')})
            return result.model_dump(mode='json')
        except Exception as exc:
            code=error_code(exc);raise
        finally:
            # Both success and failed actual official calls have durable host observations.
            # B06 raw transport observations remain separate, unchanged evidence.
            value=result.model_dump(mode='json') if result is not None else None
            record=TraceRecord(context=ctx,phase='BROKER',server_id='official-falkordb',server_version='1.3.0',
                tool_name=name.removeprefix('official::'),inventory_version=self.inventory_hash,schema_sha256=digest(next(t['input_schema'] for t in self.catalog() if t['name']==name)),
                arguments_sha256=digest(args),output_sha256=digest(value) if value else None,validated_output=code=='SUCCESS',
                started_at=started,finished_at=utc_now(),latency_ms=(time.perf_counter()-clock)*1000,status=code,
                error_code=None if code=='SUCCESS' else code,graph_revision=result.graph_revision if result else None,rationale_summary=summary)
            await asyncio.to_thread(self.store.append,record)
