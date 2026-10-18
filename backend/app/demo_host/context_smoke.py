"""One independent read-only provider-format probe; never resume a workflow."""
import copy
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4
from app.agents.checkpoints import saver
from app.agents.models import InvestigationState
from app.agents.mcp import brokers
from app.agents.runtime import InvestigationAgent
from app.agents.provider import Gemini
from app.agents.policy import Permit
from app.graph.models import digest
from app.graph.queries import GraphQueries
from app.graph.schema import utc_now
from app.mcp.civicly.contracts import Context
from cli.private import write_private,read_json
from .runtime import HostBlocked,local_preflight,model_preflight,provider_settings
from .source import source_writer


def read_only_selection(selection,catalog):
    if selection.action!='READ':raise HostBlocked('PROBE_DID_NOT_SELECT_READ')
    if selection.tool_name not in {t['name'] for t in catalog}:raise HostBlocked('PROBE_TOOL_NOT_DISCOVERED')
    from app.mcp.policy import ALLOWED
    from app.mcp.civicly.contracts import READ
    allowed={'official::'+name for name in ALLOWED}|{'civicly::'+name for name in READ}
    if selection.tool_name not in allowed:raise HostBlocked('PROBE_TOOL_NOT_READ_ONLY')


def read_status(name,result):
    if name.startswith('official::'):
        from app.mcp.models import ReadResult
        ReadResult.model_validate(result)
        return 'SUCCESS'
    return result.get('status','ERROR')


def verify_smoke(config,profile,repo):
    """Nonbillable readback of the original paid attempt; no retry or receipt mutation."""
    from app.mcp.civicly.runtime import connections
    from app.mcp.civicly.storage import TraceStore
    from app.agents.spending import Ledger
    parent=Path(config.auth_store).parent
    paths=[parent/('context-wire-smoke'+suffix+'.json') for suffix in ['-receipt','-failure']]
    path=next((p for p in paths if p.exists()),None)
    if path is None:raise HostBlocked('CONTEXT_SMOKE_RECEIPT_UNAVAILABLE')
    proof=read_json(path,private=True)
    case=next((c for c in config.cases if c.investigation_id==proof['investigation_id']),None)
    if case is None or proof['source_graph']!=profile.graph or case.thread_id!=proof['original_workflow_thread_id']:raise HostBlocked('CONTEXT_SMOKE_VERIFY_SCOPE')
    selection=__import__('app.agents.models',fromlist=['Selection']).Selection.model_validate(proof['selection'])
    read_only_selection(selection,[{'name':selection.tool_name}])
    saved=saver(profile).get_tuple({'configurable':{'thread_id':case.thread_id}})
    if saved is None or saved.config['configurable']['checkpoint_id']!=proof['original_checkpoint_id'] or digest(saved.checkpoint['channel_values']['data'])!=proof['original_checkpoint_sha256']:raise HostBlocked('CONTEXT_SMOKE_CHECKPOINT_CHANGED')
    if saver(profile).get_tuple({'configurable':{'thread_id':proof['probe_thread_id']}}) is not None:raise HostBlocked('CONTEXT_SMOKE_UNEXPECTED_CHECKPOINT')
    if GraphQueries(repo)._state()!=proof['source_revision_before']:raise HostBlocked('CONTEXT_SMOKE_SOURCE_CHANGED')
    with connections() as (_,writer,name):record=TraceStore(writer,name).get(proof['mcp_read']['execution_id'])
    if record is None or record.phase!='BROKER' or record.status!='SUCCESS' or not record.validated_output:raise HostBlocked('CONTEXT_SMOKE_TRACE_NOT_SUCCESSFUL')
    if (record.context.source_graph,record.context.investigation_id,record.context.trace_id)!=(profile.graph,case.investigation_id,proof['probe_thread_id']):raise HostBlocked('CONTEXT_SMOKE_TRACE_SCOPE')
    if record.output_sha256!=proof['mcp_read']['output_sha256'] or record.arguments_sha256!=digest(selection.arguments):raise HostBlocked('CONTEXT_SMOKE_TRACE_HASH')
    usage=proof['usage']
    if usage.get('model_version')!=config.model or usage.get('context_encoding',{}).get('version')!='CONTEXT-WIRE-1':raise HostBlocked('CONTEXT_SMOKE_MODEL_OR_FORMAT')
    with Ledger().db() as db:
        for request in usage['requests']:
            row=db.execute('SELECT case_id,thread,status,charged FROM requests WHERE id=?',(request['request_id'],)).fetchone()
            if row is None or (row['case_id'],row['thread'],row['status'])!=(case.investigation_id,proof['probe_thread_id'],'SETTLED') or row['charged'] is None:raise HostBlocked('CONTEXT_SMOKE_ACCOUNTING_UNSETTLED')
    return {**proof,'status':'PASS_VERIFIED_FROM_DURABLE_READBACK','verified_at':utc_now(),
        'mcp_read':{**proof['mcp_read'],'status':record.status},'actual_broker_trace':record.model_dump(mode='json'),
        'original_checkpoint_unchanged':True,'source_revision_unchanged':True,'persistent_probe_checkpoint_created':False,
        'paid_retry_performed':False,'read_redispatched':False,'initial_harness_failure_retained':path.name.endswith('-failure.json')}


async def smoke(config,profile,repo,case_id,*,live=False):
    if live is not True:raise HostBlocked('EXPLICIT_CONTEXT_SMOKE_LIVE_REQUIRED')
    case=next((c for c in config.cases if c.investigation_id==case_id),None)
    if case is None:raise HostBlocked('CASE_NOT_HOST_AUTHORIZED')
    marker=Path(config.auth_store).parent/'context-wire-smoke.json'
    if marker.exists():raise HostBlocked('CONTEXT_SMOKE_ALREADY_ATTEMPTED_REVIEW_RECEIPT')
    with source_writer(repo):
        local_preflight(config,profile,repo,case_id=case_id)
        compatibility=await model_preflight(config)
        saved=saver(profile).get_tuple({'configurable':{'thread_id':case.thread_id}})
        if saved is None:raise HostBlocked('CONTEXT_SMOKE_REQUIRES_SAVED_CONTEXT')
        original=copy.deepcopy(saved.checkpoint['channel_values']['data'])
        state=InvestigationState.model_validate(original);state.as_of=utc_now()
        revision=GraphQueries(repo)._state();probe_thread='CONTEXT-SMOKE-'+uuid4().hex
        async with brokers(profile,config.profile,memory_path=config.memory_profile) as tools:
            tools.bind_inventory(state.inventory_hash)
            agent=InvestigationAgent(profile,repo,tools,SimpleNamespace(),saver(profile))
            context=agent.context(state)
            context['state']['thread_id']=probe_thread
            context['read_only_probe']={'kind':'INDEPENDENT_PROVIDER_FORMAT_SMOKE_NOT_WORKFLOW_RESUME',
                'instruction':'This is a separate read-only compatibility probe. Resolve the encoded context and choose one discovered READ to inspect a current infrastructure/source reference relevant to the existing investigation, or PAUSE if unavailable. No PROPOSE, ASSESS, INSPECT, RECOMMEND, approval, work or field write is authorized. Existing workflow is not resumed. Stop after one selection and at most one real MCP read.',
                'original_workflow_thread_id':case.thread_id,'original_checkpoint_id':saved.config['configurable']['checkpoint_id']}
            settings=provider_settings(config).model_copy(update={'context_wire':True,'max_output_tokens':1024})
            permit=Permit.explicit_live(approved=True,investigation_id=case_id,thread_id=probe_thread,milestone='DEMO-CONTEXT-SMOKE')
            model=Gemini(settings,permit=permit)
            remaining=min(50000,state.budget.max_tokens-state.tokens)
            if remaining<4096:raise HostBlocked('CONTEXT_SMOKE_EXISTING_BUDGET_INSUFFICIENT')
            proof={'status':'DISPATCHING','mode':'GENUINE_GEMINI_READ_ONLY_PROBE','investigation_id':case_id,
                'probe_thread_id':probe_thread,'original_workflow_thread_id':case.thread_id,'source_graph':profile.graph,
                'original_checkpoint_id':saved.config['configurable']['checkpoint_id'],'original_checkpoint_sha256':digest(original),
                'source_revision_before':revision,'model_compatibility':compatibility,'workflow_resumed':False,
                'domain_actions_authorized':False,'automatic_retry':False,'maximum_selections':1,'maximum_mcp_reads':1}
            write_private(marker,proof)
            try:
                async with model.execution_scope(probe_thread,case_id):
                    selection,tokens=await model.choose(context,remaining)
                    proof.update(selection=selection.model_dump(mode='json'),usage=model.last_usage,accounted_tokens=tokens)
                    write_private(marker.with_name(marker.stem+'-selection.json'),proof)
                    read_only_selection(selection,tools.catalog())
                    ctx=Context(trace_id=probe_thread,execution_id='CONTEXT-READ-'+uuid4().hex,investigation_id=case_id,
                        source_graph=profile.graph,caller_role='READ_ONLY',invocation_origin='APPLICATION')
                    result=await tools.call(selection.tool_name,selection.arguments,ctx,selection.summary,cutoff=state.as_of)
                    proof['mcp_read']={'tool_name':selection.tool_name,'arguments_sha256':digest(selection.arguments),
                        'execution_id':ctx.execution_id,'status':read_status(selection.tool_name,result),'output_sha256':digest(result),
                        'source_evidence_ids':result.get('source_evidence_ids',[]),'graph_path_count':len(result.get('data',{}).get('paths',[]))}
                after=saver(profile).get_tuple({'configurable':{'thread_id':case.thread_id}})
                if after.config['configurable']['checkpoint_id']!=proof['original_checkpoint_id'] or digest(after.checkpoint['channel_values']['data'])!=proof['original_checkpoint_sha256']:raise HostBlocked('CONTEXT_SMOKE_CHECKPOINT_CHANGED')
                if GraphQueries(repo)._state()!=revision:raise HostBlocked('CONTEXT_SMOKE_SOURCE_CHANGED')
                if read_status(selection.tool_name,result) not in {'SUCCESS','PARTIAL'}:raise HostBlocked('CONTEXT_SMOKE_READ_NOT_SUCCESSFUL')
                if model.last_usage.get('context_encoding',{}).get('version')!='CONTEXT-WIRE-1':raise HostBlocked('CONTEXT_SMOKE_WIRE_NOT_USED')
                proof.update(status='PASS',original_checkpoint_unchanged=True,source_revision_unchanged=True,
                    persistent_probe_checkpoint_created=False,spending=model.spending())
                write_private(marker.with_name(marker.stem+'-receipt.json'),proof)
                return proof
            except Exception:
                # Retain marker/known selection and all reservations; never retry a probe automatically.
                write_private(marker.with_name(marker.stem+'-failure.json'),{**proof,'status':'STOPPED_REQUIRES_REVIEW','usage':model.last_usage,'spending':model.spending(),'raw_exception_exported':False})
                raise
