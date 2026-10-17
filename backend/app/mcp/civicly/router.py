"""Trusted runtime routing with distinct namespaces and controlled official traces."""
import asyncio,time
from contextlib import asynccontextmanager
from app.mcp.broker import open_broker,BrokerError,error_code
from app.mcp.policy import ALLOWED
from app.graph.schema import utc_now
from .broker import open_domain
from .contracts import context,digest
from .models import TraceRecord
from .runtime import connections
from .storage import TraceStore

class RuntimeBroker:
    def __init__(self,official,domain,store,official_traces):
        self.__official=official;self.__domain=domain;self.__store=store
        self.__schemas={t['name']:t['official_schema_sha256'] for t in official.tools()}
        self.__inventory=next(t['inventory_sha256'] for t in official_traces if t['operation']=='tools/list')
        self.__protocol=next(t['protocol_version'] for t in official_traces if t['operation']=='initialize')
    def tools(self):
        return self.__domain.tools()+[{'name':'official::'+t['name'],'broker_request_schema':t['broker_request_schema']} for t in self.__official.tools()]
    async def call(self,name,args):
        if isinstance(name,str) and name.startswith('civicly::'):return await self.__domain.call(name,args)
        c=context();started,clock=utc_now(),time.perf_counter();code='SUCCESS';result=None
        tool=name.removeprefix('official::') if isinstance(name,str) else ''
        try:
            if not isinstance(name,str) or not name.startswith('official::') or tool not in ALLOWED:raise BrokerError('DENIED_TOOL')
            if not isinstance(args,dict) or 'tool' in args:raise BrokerError('INVALID_ARGUMENTS')
            result=await self.__official.call({'tool':tool,**args});return result.model_dump(mode='json')
        except Exception as exc:
            code=error_code(exc);raise BrokerError(code) from None
        finally:
            record=TraceRecord(context=c,phase='BROKER',server_id='official-falkordb',server_version='1.3.0',tool_name=tool if tool in ALLOWED else 'UNAUTHORIZED_TOOL',
                inventory_version=self.__inventory,schema_sha256=self.__schemas.get(tool,digest({})),arguments_sha256=digest(args),
                started_at=started,finished_at=utc_now(),latency_ms=(time.perf_counter()-clock)*1000,status=code,error_code=None if code=='SUCCESS' else code,
                protocol_version=self.__protocol,validated_output=code=='SUCCESS',output_sha256=digest(result.model_dump(mode='json')) if result and code=='SUCCESS' else None,
                graph_revision=result.graph_revision if result and code=='SUCCESS' else None,result_summary={'rows':len(result.rows or [])} if result else {})
            try:await asyncio.to_thread(self.__store.append,record)
            except Exception:raise BrokerError('TRACE_PERSISTENCE_FAILED') from None

@asynccontextmanager
async def open_runtime():
    with connections() as (_,writer,name):
        store=TraceStore(writer,name)
        official_traces=[]
        async with open_broker(official_traces) as official,open_domain() as domain:
            yield RuntimeBroker(official,domain,store,official_traces)
