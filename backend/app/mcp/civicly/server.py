"""Actual official Python SDK low-level MCP server; registered READ handlers only."""
import asyncio,json,time
from uuid import uuid4
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from mcp import types
from app.graph.schema import utc_now
from app.graph.repository import NotFound
from .contracts import READ,SERVER,VERSION,SCHEMA_VERSION,INVENTORY_HASH,Context,context,input_schema,validate,bounded,digest
from .models import TraceRecord
from .runtime import connections
from .service import CivicReadService
from .storage import TraceStore


def trace(ctx,name,started,clock,args_hash,result=None,error=None):
    return TraceRecord(context=ctx,phase='SERVER',server_id=SERVER,server_version=VERSION,tool_name=name if name in READ else 'UNAUTHORIZED_TOOL',
        inventory_version=INVENTORY_HASH,schema_sha256=digest(input_schema(name,True)) if name in READ else digest({}),
        arguments_sha256=args_hash,started_at=started,finished_at=utc_now(),latency_ms=(time.perf_counter()-clock)*1000,
        status=result['status'] if result else 'PERMISSION_DENIED',error_code=error or (result['error']['code'] if result and result['error'] else None),validated_output=result is not None,
        output_sha256=digest(result) if result else None,graph_revision=result['graph_revision'] if result else None,
        source_evidence_ids=result['source_evidence_ids'] if result else [],
        graph_path_ids=[p['id'] for p in result['data']['paths']] if result else [],
        result_summary={'nodes':len(result['data']['nodes']),'edges':len(result['data']['edges']),'truncated':result['truncated']} if result else {})


def build(service,store,*,expected_graph=None):
    async def listing(ctx,params):
        return types.ListToolsResult(tools=[types.Tool(name=name,description=t['description'],input_schema=input_schema(name,True),output_schema=t['output_schema']) for name,t in sorted(READ.items())])
    async def execute(request,params):
        started,clock=utc_now(),time.perf_counter();name=params.name;args=params.arguments or {};c=context();result=None;error=None
        try:
            if name not in READ:raise PermissionError('DENIED_TOOL')
            bounded(args);validate(input_schema(name,True),args)
            c=Context.model_validate(args['_context'])
            if expected_graph is not None and c.source_graph!=expected_graph:raise PermissionError('SOURCE_MISMATCH')
            values={k:v for k,v in args.items() if k!='_context'}
            if values.get('investigation_id') and c.investigation_id!=values['investigation_id']:raise PermissionError('CONTEXT_MISMATCH')
            try:result=await asyncio.to_thread(service.run,name,values,c)
            except NotFound:
                result=service.result(name,c,values.get('as_of',utc_now()));result.update(status='UNAVAILABLE',error={'code':'DATA_UNAVAILABLE','message':'Requested sourced record is absent','retryable':False})
                result['data']['gaps'].append('Requested record/history does not exist in accepted dataset')
            except Exception:
                result=service.result(name,c,values.get('as_of',utc_now()));result.update(status='ERROR',error={'code':'READ_FAILED','message':'Read failed closed; no state change','retryable':True})
                result['data']['gaps'].append('Read failed validation, temporal, revision or availability checks')
            validate(READ[name]['output_schema'],result)
        except Exception:
            error='DENIED_TOOL' if name not in READ else 'INVALID_ARGUMENTS'
        try:arg_hash=digest(args)
        except Exception:arg_hash=digest({'withheld':True})
        record=trace(c,name,started,clock,arg_hash,result,error)
        # Persistence must succeed before a result is acknowledged. No false success
        # if lease/DB/unknown write outcome fails; SDK returns a protocol tool error.
        await asyncio.to_thread(store.append,record)
        if result is None:
            return types.CallToolResult(is_error=True,content=[types.TextContent(type='text',text=json.dumps({'code':error,'trace_id':c.trace_id,'execution_id':c.execution_id}))])
        return types.CallToolResult(content=[types.TextContent(type='text',text=json.dumps(result))],structured_content=result,is_error=False)
    lock=asyncio.Lock();calls=0
    async def call(request,params):
        nonlocal calls
        async with lock:
            if calls>=64:
                return types.CallToolResult(is_error=True,content=[types.TextContent(type='text',text=json.dumps({'code':'SERVER_CALL_BUDGET'}))])
            calls+=1
            return await execute(request,params)
    return Server(SERVER,version=VERSION,on_list_tools=listing,on_call_tool=call)


async def main():
    with connections() as (reader,writer,name):
        from app.memory.runtime import configured
        server=build(CivicReadService(reader,memory_profile=configured(CivicReadService(reader).repo.graph.name)),TraceStore(writer,name),expected_graph=CivicReadService(reader).repo.graph.name)
        async with stdio_server() as streams:
            await server.run(*streams,server.create_initialization_options())


if __name__=='__main__':asyncio.run(main())
