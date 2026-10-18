"""One real StateGraph, actual broker-selected reads and controlled B09 actions."""
import asyncio,json,time,hashlib
from typing import TypedDict
from langgraph.graph import StateGraph,START
from langgraph.types import interrupt,Command
from .isolation import agent_files
from app.active import active_scope
from app.graph.queries import GraphQueries
from app.graph.schema import utc_now
from app.graph.models import digest
from app.services.evidence import EvidenceService,Actor
from app.services.evidence.policies import POLICIES
from app.services.evidence.reader import Reader
from app.mcp.civicly.contracts import Context
from .models import InvestigationState,Selection
from .control import Control,identity
from .checkpoints import ownership,RecoveryRequired

class Channels(TypedDict):
    data:dict

class InvestigationAgent:
    def __init__(self,profile,repo,tools,model,checkpointer,*,clock=utc_now,planning_service=None):
        if repo.graph.name!=profile.graph or tools.graph!=profile.graph:raise ValueError('Active graph mismatch')
        self.profile,self.repo,self.tools,self.model,self.saver,self.clock=profile,repo,tools,model,checkpointer,clock
        if hasattr(tools,'bind_read_cache'):tools.bind_read_cache(self.revision)
        self.planning_service=planning_service
        self.control=Control(repo,clock);self.service=EvidenceService(repo,clock=clock);self.check=lambda:None
        graph=StateGraph(Channels)
        for name,handler in [('Supervisor',self.supervisor),('Investigator',self.investigator),('RootCauseAnalyst',self.analyst),('ResolutionPlanner',self.planner),('Coordinator',self.coordinator),('AwaitDependency',self.await_dependency)]:graph.add_node(name,handler)
        graph.add_edge(START,'Supervisor')
        graph.add_conditional_edges('Supervisor',self.route,{'READ':'Investigator','PROPOSE':'RootCauseAnalyst','ASSESS':'RootCauseAnalyst','INSPECT':'Coordinator','RECOMMEND':'ResolutionPlanner','PAUSE':'Coordinator'})
        for name in ['Investigator','RootCauseAnalyst']:graph.add_edge(name,'Supervisor')
        graph.add_edge('ResolutionPlanner','Coordinator');graph.add_edge('Coordinator','AwaitDependency');graph.add_edge('AwaitDependency','Supervisor')
        self.graph=graph.compile(checkpointer=checkpointer)
    def revision(self):return GraphQueries(self.repo)._state()
    def decode(self,channel):
        state=InvestigationState.model_validate(channel['data'])
        if state.graph!=self.profile.graph or state.inventory_hash!=self.tools.inventory_hash:raise RecoveryRequired('CHECKPOINT_SCOPE_OR_INVENTORY_CHANGED')
        if self.repo.get_node(state.investigation_id,'Investigation').properties.get('thread_id')!=state.thread_id:raise RecoveryRequired('THREAD_BINDING_MISMATCH')
        reader=Reader(self.repo,self.clock())
        bound={e.target for e in reader.edges('INVESTIGATES',source=state.investigation_id)}
        if not set(state.incident_ids+[state.problem_cluster_id])<=bound:raise RecoveryRequired('CHECKPOINT_INCIDENT_BINDING_MISMATCH')
        known={e.target for e in reader.edges('PROPOSES',source=state.investigation_id)}
        if not set(state.hypotheses)<=known:raise RecoveryRequired('CHECKPOINT_HYPOTHESIS_BINDING_MISMATCH')
        if state.current_plan_id is not None:
            from app.services.planning.storage import Store
            saved=Store(self.repo).get(state.current_plan_id)
            if not saved or saved['draft']['investigation_id']!=state.investigation_id or saved['receipt']['version']!=state.current_plan_version or saved['receipt']['plan_hash']!=state.current_plan_hash:raise RecoveryRequired('CHECKPOINT_PLAN_BINDING_MISMATCH')
        self.check();return state
    def output(self,s,node):
        s.phase=node;s.nodes.append(node)
        return {'data':s.model_dump(mode='json')}
    @staticmethod
    def route(channel):return channel['data']['selection']['action']
    @staticmethod
    def action_schemas():
        from app.services.evidence.models import Propose,Assess,RequestInspection
        result={}
        host={'operation','request_id','investigation_id','incident_ids','expected_hash','as_of'}
        for name,model in [('PROPOSE',Propose),('ASSESS',Assess),('INSPECT',RequestInspection)]:
            schema=model.model_json_schema()
            schema['properties']={k:v for k,v in schema['properties'].items() if k not in host}
            schema['required']=[k for k in schema.get('required',[]) if k not in host]
            result[name]=schema
        from app.services.planning.models import PlanDraft
        result['RECOMMEND']={'type':'object','additionalProperties':False,'required':['plan_draft'],'properties':{'plan_draft':PlanDraft.model_json_schema()}}
        return result
    def context(self,s):
        r=Reader(self.repo,s.as_of);hypotheses=[]
        for id in s.hypotheses:
            n=r.node(id,'Hypothesis');history=self.service.history(id,s.as_of)
            hypotheses.append({'id':id,'definition':n.properties,'assessments':[h.model_dump(mode='json') for h in history]})
        from .context import build
        context=build(s,hypotheses,self.tools.catalog(),POLICIES[s.issue],self.action_schemas(),
            self.repo._read('MATCH (d:Department {municipality_id:$scope}) RETURN d.id LIMIT 10',{'scope':'demo-city'}),
            self.model.spending() if hasattr(self.model,'spending') and self.model.permit is not None else None)
        from app.services.planning.policy import ACTIONS
        context['planning_action_policies']={k:v for k,v in ACTIONS.items() if v['issue']==s.issue}
        from .inspection_context import requested_inspections
        context['requested_inspections']=requested_inspections(self.service,s)
        context['inspection_status_guidance']='state.pending_inspections retains request IDs from earlier checkpoints. Use requested_inspections for current lifecycle status. A COMPLETED request is not still awaiting field work. Its report references are metadata, not causal proof: retrieve the actual report/findings through an approved MCP read such as get_maintenance_history for the requested asset before reassessment. If no registered evidence can be retrieved, state that limitation.'
        context['planning_guards']='Remedial proposals require reviewed target-specific causal support and explicit causal inspection/safety conditions. SUPPORTED_NOW: both MET with validated report evidence and no future task dependencies. CONDITIONAL: any unmet causal inspection must depend on a target-covering INSPECTION task; safety remains an explicit unresolved gate. Insufficient/contradicted support: INSPECTION only. All procedures PROPOSED, no execution authority. Use planning_feedback for later authorized clarification; never auto-replan on operator recovery.'
        return context

    async def supervisor(self,channel):
        s=self.decode(channel);s.as_of=self.clock();s.iterations+=1
        if s.pause_reason is not None:
            s.selection=Selection(action='PAUSE',summary='A dependency or action requires operator recovery',tool_name='',arguments_json='{}',pause_reason='DEPENDENCY_UNAVAILABLE')
            return self.output(s,'Supervisor')
        if s.iterations>s.budget.max_iterations or time.monotonic()-self.started>s.budget.max_seconds or s.tokens>=s.budget.max_tokens:
            s.selection=Selection(action='PAUSE',summary='Runtime budget exhausted; operator review required',tool_name='',arguments_json='{}',pause_reason='DEPENDENCY_UNAVAILABLE')
            s.pause_reason='BUDGET_EXHAUSTED';return self.output(s,'Supervisor')
        id=identity('DEC',s.thread_id,s.iterations,s.wakes);saved=self.control.selected(id)
        accounted=False
        try:
            if saved:selection,metadata=saved;used=metadata['tokens']
            else:
                selection,used=await self.model.choose(self.context(s),s.budget.max_tokens-s.tokens)
                if not isinstance(selection,Selection) or type(used)is not int or used<0:raise ValueError('Invalid model adapter result')
                metadata={'mode':self.model.mode,'tokens':used,'inventory_hash':s.inventory_hash,'graph_revision':self.revision(),'as_of':s.as_of,
                          'usage':getattr(self.model,'last_usage',{}),'provider_failure':getattr(self.model,'last_failure',None),'prompt_sha256':hashlib.sha256(__import__('app.agents.provider',fromlist=['PROMPT']).PROMPT.encode()).hexdigest(),'investigation_id':s.investigation_id,'thread_id':s.thread_id}
                self.check();self.control.decision(id,selection,metadata)
            s.tokens+=used;accounted=True;s.selection=selection
            if id not in s.decisions:s.decisions.append(id)
            if s.refresh_required and selection.action not in {'READ','PAUSE'}:raise ValueError('Fresh MCP read required after revision change')
        except Exception as e:
            if type(e).__name__=='ProviderError' and not accounted:s.tokens+=getattr(self.model,'last_usage',{}).get('accounted_tokens',getattr(self.model,'last_usage',{}).get('total_tokens',0))
            if type(e).__name__=='ProviderError':
                s.observations.append({'provider_failure':getattr(self.model,'last_failure',None),'provider_usage':getattr(self.model,'last_usage',{}),'status':'ERROR','host_generated':True})
                if e.code in {'TOKEN_BUDGET','PROJECT_SPENDING_CAP','INVESTIGATION_SPENDING_CAP','LEDGER_RECONCILIATION_REQUIRED','PROVIDER_INPUT_LIMIT'}:s.pause_reason=e.code
            s.errors.append(getattr(e,'code',str(e) if type(e).__name__=='ProviderError' else 'INVALID_MODEL_SELECTION'))
            s.selection=Selection(action='PAUSE',summary='Model or resume validation failed; no action executed',tool_name='',arguments_json='{}',pause_reason='DEPENDENCY_UNAVAILABLE')
        s.graph_revision=self.revision();return self.output(s,'Supervisor')
    def begin(self,s):
        self.check()
        if self.revision()!=s.graph_revision:raise RecoveryRequired('SOURCE_CHANGED_BEFORE_ACTION')
        if not s.decisions:raise ValueError('Durable decision missing')
        id=identity('EV',s.thread_id,s.iterations,s.wakes)
        fresh=self.control.journal(id)[0] is None
        node,value=self.control.prepare(id,s.decisions[-1],s.selection)
        return node,value,fresh
    def compact(self,value):
        # Context projection removes duplication; full validated result stays durable.
        return value
    def apply(self,s,result):
        s.observations.append(result)
        for gap in result.get('data',{}).get('gaps',result.get('gaps',[])):
            if gap not in s.missing_evidence and len(s.missing_evidence)<100:s.missing_evidence.append(gap)
        ids=set(result.get('source_evidence_ids',[]))
        if result.get('assessment'):ids.update(ref['id'] for ref in result['assessment'].get('evidence_references',[]))
        for id in ids:s.evidence[id]=self.repo.get_node(id,'Evidence').content_hash
        s.graph_revision=self.revision()
    async def investigator(self,channel):
        s=self.decode(channel)
        if s.tool_calls>=s.budget.max_tools:
            s.errors.append('TOOL_BUDGET');s.selection=Selection(action='PAUSE',summary='Tool budget exhausted',tool_name='',arguments_json='{}',pause_reason='DEPENDENCY_UNAVAILABLE')
            s.pause_reason='TOOL_BUDGET';return self.output(s,'Investigator')
        journal,value,fresh=self.begin(s)
        if value['status']=='COMMITTED':result=value['result']
        elif not fresh:
            s.errors.append('UNCERTAIN_TOOL_ACTION');s.pause_reason='RECOVERY_REQUIRED';return self.output(s,'Investigator')
        else:
            execution=identity('MCP',s.thread_id,s.iterations,s.wakes)
            ctx=Context(trace_id=s.thread_id,execution_id=execution,parent_execution_id=s.decisions[-1],investigation_id=s.investigation_id,source_graph=s.graph,caller_role='READ_ONLY',invocation_origin='APPLICATION')
            try:
                result=await self.tools.call(s.selection.tool_name,s.selection.arguments,ctx,s.selection.summary,cutoff=s.as_of)
                # Official node templates intentionally return current raw facts. Reuse
                # accepted B05 temporal rules before any such facts enter model context.
                from app.graph.analysis.reader import Reader as AnalysisReader
                from app.graph.analysis.models import AnalysisRequest,AnalysisLimits
                from app.mcp.broker import BrokerError
                temporal=AnalysisReader(self.repo,AnalysisRequest(operation='dependencies',ids=(s.asset_ids[0],),as_of=s.as_of),AnalysisLimits(),{})
                rows=[*(result.get('rows') or []),*result.get('data',{}).get('nodes',[]),*result.get('data',{}).get('edges',[])]
                if any('properties' in row and not temporal.visible(row['properties']) for row in rows):raise BrokerError('OUTPUT_OUTSIDE_CUTOFF')
                result=self.compact(result)
                if getattr(self.tools,'last_cache_receipt',None):result={**result,'host_read_cache':self.tools.last_cache_receipt}
            except Exception as e:result={'status':'ERROR','error':{'code':getattr(e,'code','INVALID_ARGUMENTS')},'source_evidence_ids':[],'gaps':['MCP failed closed; reconnect at next wake']}
            self.check();self.control.commit(journal,value,result)
            if await asyncio.to_thread(self.tools.store.get,execution) is not None and execution not in s.executions:s.executions.append(execution)
        self.apply(s,result);s.tool_calls+=1
        if result.get('status')=='ERROR':s.pause_reason='DEPENDENCY_UNAVAILABLE'
        else:s.refresh_required=False
        return self.output(s,'Investigator')
    async def domain_action(self,s,operation):
        journal,value,fresh=self.begin(s)
        if value['status']=='COMMITTED':result=value['result']
        else:
            args=s.selection.arguments
            allowed={'propose':{'cause_code','asset_ids','statement','mechanism','confirming_codes','falsifying_codes','topology'},'assess':{'hypothesis_id','evidence_ids'},'request_inspection':{'asset_ids','department_id','inspection_type'}}[operation]
            if set(args)-allowed:raise ValueError('Unapproved analytical arguments')
            command={**args,'operation':operation,'request_id':journal.id}
            if operation in {'propose','request_inspection'}:command['investigation_id']=s.investigation_id
            if operation=='propose':command['incident_ids']=s.incident_ids
            if operation=='assess':
                if args['hypothesis_id'] not in s.hypotheses:raise ValueError('Hypothesis outside current investigation')
                command.update(expected_hash=self.repo.get_node(args['hypothesis_id'],'Hypothesis').content_hash,as_of=s.as_of)
            # B09 owns all judgments and native request-id replay. Save original command
            # before dispatch; uncertain PREPARED action requires operator reconciliation.
            if value.get('command') and value['command']!=command:raise RecoveryRequired('STALE_DOMAIN_REPLAY')
            if not value.get('command'):
                value={**value,'command':command}
                self.check()
                journal=self.repo.update_node(journal.id,{'summary':json.dumps(value),'updated_at':self.clock()},expected_hash=journal.content_hash)
            self.check()
            receipt=self.service.execute(value['command'],Actor(id='civicly-b10-analyst',role='ANALYST'))
            result=receipt.model_dump(mode='json');self.check();self.control.commit(journal,value,result)
        if operation=='propose' and result['entity_id'] not in s.hypotheses:s.hypotheses.append(result['entity_id'])
        if operation=='request_inspection' and result['entity_id'] not in s.pending_inspections:s.pending_inspections.append(result['entity_id'])
        self.apply(s,result)
    async def analyst(self,channel):
        s=self.decode(channel)
        try:await self.domain_action(s,'propose' if s.selection.action=='PROPOSE' else 'assess')
        except Exception as e:
            s.errors.append(getattr(e,'code','ANALYTICAL_ACTION_REJECTED'))
            from app.graph.repository import OutcomeUnknown
            if isinstance(e,(OutcomeUnknown,RecoveryRequired)):
                s.pause_reason='RECOVERY_REQUIRED'
        return self.output(s,'RootCauseAnalyst')
    async def planner(self,channel):
        s=self.decode(channel);args=s.selection.arguments
        if set(args)=={'plan_draft'}:
            connection=None
            try:
                from app.services.planning.service import PlanningService,PlanningBlocked
                service=self.planning_service
                if service is None:
                    from app.memory.runtime import configured
                    capability=configured(s.graph)
                    if capability is None:
                        from app.services.planning.service import PlanningBlocked
                        raise PlanningBlocked('PROCEDURE_CAPABILITY_UNAVAILABLE')
                    connection,memory=capability.connect();service=PlanningService(self.repo,memory,clock=self.clock)
                if args['plan_draft'].get('investigation_id')!=s.investigation_id or args['plan_draft'].get('issue')!=s.issue:raise PlanningBlocked('PLAN_SCOPE_MISMATCH')
                self.check()
                receipt=await service.create(args['plan_draft'],request_id=identity('PLANREQ',s.thread_id,s.iterations,s.wakes),actor=Actor(id='civicly-b12-planner',role='ANALYST'))
                s.planning_feedback=None
                s.current_plan_id=receipt.id;s.current_plan_version=receipt.version;s.current_plan_hash=receipt.plan_hash
                s.observations.append({'operation':'PLAN_DRAFTED','receipt':receipt.model_dump(mode='json'),'human_review_required':True})
                s.graph_revision=self.revision();s.pause_reason='HUMAN_REVIEW'
            except Exception as error:
                from app.services.planning.feedback import feedback
                from app.graph.repository import OutcomeUnknown
                detail=feedback(error).model_dump(mode='json')
                # Unsafe writes/lease failures must reach the existing wake quarantine.
                # A failed/lost checkpoint cannot truthfully persist new feedback.
                if isinstance(error,(RecoveryRequired,OutcomeUnknown)) or detail['draft_committed']=='UNKNOWN':
                    recovery=RecoveryRequired('PLAN_OPERATOR_RECOVERY_REQUIRED')
                    from app.services.planning.service import PlanRecoveryRequired
                    if isinstance(error,PlanRecoveryRequired):recovery.reconciliation=dict(error.reconciliation)
                    raise recovery from None
                self.check()
                s.planning_feedback=feedback(error);s.observations.append({'operation':'PLAN_DRAFT_REJECTED','feedback':detail})
                s.errors.append('PLAN_DRAFT_REJECTED');s.pause_reason='PLAN_OPERATOR_RECOVERY_REQUIRED' if detail['resolution']=='OPERATOR_RECOVERY' else 'PLAN_CLARIFICATION_REQUIRED'
            finally:
                if connection is not None:connection.connection.close();connection.connection.connection_pool.disconnect()
            return self.output(s,'ResolutionPlanner')
        if set(args)!={'next_action','target_ids','basis_evidence_ids','limitations'} or not isinstance(args['next_action'],str) or len(args['next_action'])>2000 or not isinstance(args['limitations'],list):
            s.errors.append('INVALID_RECOMMENDATION')
        elif not set(args['target_ids'])<=set(s.asset_ids) or not set(args['basis_evidence_ids'])<=set(s.evidence):s.errors.append('UNSUPPORTED_RECOMMENDATION_REFERENCES')
        elif len(s.hypotheses)<2:s.errors.append('COMPETING_HYPOTHESES_REQUIRED')
        else:s.recommendation={**args,'binding':False,'human_review_required':True,'causal_status':'ONLY_B09_ASSESSMENTS_AUTHORITATIVE'}
        s.pause_reason='HUMAN_REVIEW';return self.output(s,'ResolutionPlanner')
    async def coordinator(self,channel):
        s=self.decode(channel)
        if s.selection.action=='INSPECT':
            try:await self.domain_action(s,'request_inspection');s.pause_reason='MISSING_EVIDENCE'
            except Exception as e:s.errors.append(getattr(e,'code','INSPECTION_REQUEST_REJECTED'));s.pause_reason='DEPENDENCY_UNAVAILABLE'
        s.pause_reason=s.pause_reason or s.selection.pause_reason or 'HUMAN_REVIEW'
        starts=[o['delivery_key'] for o in s.observations if o.get('operation')=='B15_DELIVERY_STARTED' and o.get('host_generated') is True]
        if starts and s.pause_reason not in {'RECOVERY_REQUIRED','PLAN_OPERATOR_RECOVERY_REQUIRED','DEPENDENCY_UNAVAILABLE'} and not any(o.get('operation')=='B15_DELIVERY_CONSUMED' and o.get('delivery_key')==starts[-1] for o in s.observations):s.observations.append({'operation':'B15_DELIVERY_CONSUMED','host_generated':True,'delivery_key':starts[-1]})
        return self.output(s,'Coordinator')
    async def await_dependency(self,channel):
        s=self.decode(channel)
        recovery=interrupt({'investigation_id':s.investigation_id,'thread_id':s.thread_id,'pause_reason':s.pause_reason,'pending_inspections':s.pending_inspections,'graph_revision':s.graph_revision})
        # Reexecuted on resume: no pre-interrupt side effect.
        if isinstance(recovery,dict) and recovery.get('budget_increase'):
            old=s.budget.model_dump(mode='json');s.budget=__import__('app.agents.models',fromlist=['Budget']).Budget.model_validate(recovery['budget_increase'])
            s.observations.append({'operation':'AUTHORIZED_BUDGET_INCREASE','host_generated':True,'previous':old,'current':s.budget.model_dump(mode='json'),'reason':recovery['operator_reason']})
        if isinstance(recovery,dict) and recovery.get('delivery_key'):s.observations.append({'operation':'B15_DELIVERY_STARTED','host_generated':True,'delivery_key':recovery['delivery_key']})
        s.wakes+=1;s.pause_reason=None;s.as_of=self.clock()
        current=self.revision();changed=current!=s.graph_revision or any(self.repo.get_node(id).content_hash!=h for id,h in s.evidence.items())
        s.refresh_required=changed;s.graph_revision=current
        if changed:
            from .recurrence import refresh
            s=refresh(self.repo,s)
            s.errors.append('SOURCE_CHANGED_REFRESH_REQUIRED')
        return self.output(s,'AwaitDependency')
    async def run(self,initial=None,*,thread_id,resume=False,budget_increase=None,authorized=False,operator_reason=None,delivery_key=None):
        if delivery_key is not None and (not isinstance(delivery_key,str) or not delivery_key.startswith('BATCH-B15-') or len(delivery_key)!=42):raise RecoveryRequired('INVALID_HOST_DELIVERY_KEY')
        if budget_increase is not None and (authorized is not True or not isinstance(operator_reason,str) or not operator_reason.strip() or len(operator_reason)>512):raise RecoveryRequired('BUDGET_INCREASE_REQUIRES_OPERATOR_AUTHORIZATION')
        self.started=time.monotonic();config={'configurable':{'thread_id':thread_id},'recursion_limit':150}
        # Operator input errors must not quarantine an otherwise valid paused thread.
        if budget_increase is not None:
            from .models import Budget
            candidate=Budget.model_validate(budget_increase)
            snapshot=await self.graph.aget_state(config)
            if not resume or not snapshot.values or not snapshot.next:raise RecoveryRequired('NO_PAUSED_THREAD')
            prior=Budget.model_validate(snapshot.values['data']['budget'])
            if any(getattr(candidate,k)<getattr(prior,k) for k in type(prior).model_fields):raise RecoveryRequired('BUDGET_DECREASE_OR_RESET_DENIED')
        elif resume:
            snapshot=await self.graph.aget_state(config)
            if snapshot.values and snapshot.next:
                from .models import Budget
                prior=Budget.model_validate(snapshot.values['data']['budget'])
                if snapshot.values['data']['wakes']>=prior.max_wakes:raise RecoveryRequired('WAKE_BUDGET_EXHAUSTED')
        with active_scope(self.profile),agent_files():
            async with ownership(self.repo.client,self.profile,thread_id) as check:
                self.check=check
                snapshot=await self.graph.aget_state(config)
                if resume:
                    if not snapshot.values or not snapshot.next:raise RecoveryRequired('NO_PAUSED_THREAD')
                    state=self.decode(snapshot.values)
                    if state.wakes>=(candidate.max_wakes if budget_increase is not None else state.budget.max_wakes):raise RecoveryRequired('WAKE_BUDGET_EXHAUSTED')
                    recovery={'host_resume':True}
                    if delivery_key:recovery['delivery_key']=delivery_key
                    if budget_increase is not None:
                        from .models import Budget
                        if authorized is not True or not isinstance(operator_reason,str) or not operator_reason.strip() or len(operator_reason)>512:raise RecoveryRequired('BUDGET_INCREASE_REQUIRES_OPERATOR_AUTHORIZATION')
                        increased=Budget.model_validate(budget_increase)
                        if any(getattr(increased,k)<getattr(state.budget,k) for k in type(state.budget).model_fields):raise RecoveryRequired('BUDGET_DECREASE_OR_RESET_DENIED')
                        recovery.update(budget_increase=increased.model_dump(mode='json'),operator_reason=operator_reason)
                    value=Command(resume=recovery)
                else:
                    if snapshot.values:raise RecoveryRequired('THREAD_ALREADY_EXISTS; resume explicitly')
                    if not isinstance(initial,InvestigationState) or initial.thread_id!=thread_id:raise ValueError('Initial thread mismatch')
                    self.control.bind(initial.investigation_id,thread_id)
                    if delivery_key:initial=initial.model_copy(update={'observations':[*initial.observations,{'operation':'B15_DELIVERY_STARTED','host_generated':True,'delivery_key':delivery_key}]})
                    value={'data':initial.model_dump(mode='json')}
                budget=initial.budget if initial is not None else (increased if budget_increase is not None else state.budget)
                async with asyncio.timeout(budget.max_seconds+65):
                    if hasattr(self.model,'execution_scope'):
                        selected=initial if initial is not None else state
                        try:
                            async with self.model.execution_scope(selected.thread_id,selected.investigation_id):
                                result=await self.graph.ainvoke(value,config,durability='sync')
                        except __import__('app.agents.provider',fromlist=['ProviderError']).ProviderError:
                            # Provider policy/cap errors are handled in Supervisor; session contention
                            # prevents entry and must remain a recoverable explicit denial.
                            raise
                    else:
                        result=await self.graph.ainvoke(value,config,durability='sync')
                check();self.decode(result)
                return result
