"""Offline development runtime; no provider client/permit and no human powers."""
from uuid import uuid4
from app.agents.models import InvestigationState,Selection
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver,ownership,RecoveryRequired
from app.agents.mcp import brokers
from app.services.evidence.reader import Reader

class ReadPause:
 mode='B15_DETERMINISTIC_DEVELOPMENT_NO_PROVIDER'
 def __init__(self):self.read=False
 async def choose(self,context,remaining_tokens):
  if not self.read:
   self.read=True
   return Selection(action='READ',summary='Deterministic development worker refreshes current active episode; not autonomous model reasoning',tool_name='official::query_graph_readonly',arguments_json=__import__('json').dumps({'template':'node','id':context['state']['incident_ids'][0]}),pause_reason='NONE'),0
  return Selection(action='PAUSE',summary='Deterministic development wake complete; no human authority or invented findings',tool_name='',arguments_json='{}',pause_reason='HUMAN_REVIEW'),0

class Runtime:
 def __init__(self,profile,path,repo,clock,*,model_factory=ReadPause,memory_path=None,planning_service=None,budget=None):
  self.profile,self.path,self.repo,self.clock,self.model_factory=profile,path,repo,clock,model_factory
  self.memory_path,self.planning_service,self.budget=memory_path,planning_service,budget
 def model_for(self,inv,thread):return self.model_factory()
 def thread(self,inv):return self.repo.get_node(inv,'Investigation').properties.get('thread_id') or 'B15-'+__import__('app.graph.models',fromlist=['digest']).digest(inv)[:32]
 async def probe(self,inv,key):
  thread=self.thread(inv)
  async with ownership(self.repo.client,self.profile,thread):
   try:
    saved=saver(self.profile).get_tuple({'configurable':{'thread_id':thread}})
    if not saved:return None
    state=InvestigationState.model_validate(saved.checkpoint['channel_values']['data'])
    if state.graph!=self.profile.graph or state.investigation_id!=inv or state.thread_id!=thread:raise RecoveryRequired('CONSUMER_CHECKPOINT_BINDING')
    if state.pause_reason in {'RECOVERY_REQUIRED','PLAN_OPERATOR_RECOVERY_REQUIRED','DEPENDENCY_UNAVAILABLE'}:raise RecoveryRequired('CONSUMER_RECOVERY_REQUIRED')
    if not any(o.get('operation')=='B15_DELIVERY_CONSUMED' and o.get('host_generated') is True and o.get('delivery_key')==key for o in state.observations):return None
    return {'kind':'CHECKPOINT_CONFIRMED','thread_id':thread,'investigation_id':inv,'delivery_key':key,'checkpoint_id':saved.config['configurable']['checkpoint_id'],'pause_reason':state.pause_reason,'active_incident_ids':state.incident_ids,'tool_calls':state.tool_calls}
   except RecoveryRequired:raise
   except Exception:raise RecoveryRequired('CONSUMER_CHECKPOINT_VERIFICATION_FAILED') from None
 async def handle(self,claim):
  inv=claim['case_id'];thread=self.thread(inv);saved=saver(self.profile).get_tuple({'configurable':{'thread_id':thread}})
  if not saved and self.repo.get_node(inv,'Investigation').properties.get('thread_id'):raise RecoveryRequired('BOUND_CHECKPOINT_MISSING_REQUIRES_OPERATOR')
  async with brokers(self.profile,self.path,timeout=10,memory_path=self.memory_path) as tools:
   if saved and hasattr(tools,'bind_inventory'):tools.bind_inventory(saved.checkpoint['channel_values']['data']['inventory_hash'])
   agent=InvestigationAgent(self.profile,self.repo,tools,self.model_for(inv,thread),saver(self.profile),clock=self.clock,planning_service=self.planning_service)
   if saved:await agent.run(thread_id=thread,resume=True,delivery_key=claim['key'])
   else:
    r=Reader(self.repo,self.clock());links=r.edges('INVESTIGATES',source=inv)
    incidents=[r.node(e.target) for e in links if r.node(e.target).kind=='Incident'];active=[n for n in incidents if n.properties['status'] in {'REPORTED','ACTIVE','MITIGATED'}]
    clusters=[e.target for e in links if r.node(e.target).kind=='ProblemCluster']
    issues={n.properties['issue_type'] for n in active}
    if len(issues)!=1 or len(clusters)!=1:raise RecoveryRequired('INITIAL_CASE_SCOPE_REQUIRES_OPERATOR')
    assets=sorted({e.target for n in active for e in r.edges('AFFECTS',source=n.id)})
    revision=agent.revision()
    state=InvestigationState(graph=self.profile.graph,investigation_id=inv,thread_id=thread,problem_cluster_id=clusters[0],incident_ids=[n.id for n in active],asset_ids=assets,issue=next(iter(issues)),graph_revision=revision,inventory_hash=tools.inventory_hash,as_of=self.clock())
    if self.budget is not None:state.budget=self.budget
    await agent.run(state,thread_id=thread,delivery_key=claim['key'])
  return await self.probe(inv,claim['key'])
