"""Bounded synthetic world controller. No solver, approval or outcome shortcut."""
import json
from pathlib import Path
from app.active import active_scope,load as load_profile
from app.graph.models import digest
from app.graph.repository import GraphRepository,PreconditionFailed,Conflict
from app.graph.schema import timestamp
from app.services.operations.auth import Denied
from app.services.evidence.models import Actor,Review
from app.services.evidence.service import EvidenceService
from app.services.evidence.reader import Reader
from app.services.http.service import Recovery
from .errors import DemoBlocked
from .models import ScenarioSummary,ScenarioPage,ScenarioCase
from .definitions import load,BASE,TARGETS,intake,ROOT,target
LIMITATIONS=['Synthetic world mechanics; offline worker is not genuine model evaluation','Candidate owners remain unverified; planning needs independently verified responsibility and sourced compatible procedures','Catalog historical repairs/inspections are reported claims; complete operational history requires operator workflow/B22','Utility leak repair, capacity changes and dumping-management remedial types are not implemented; do not substitute another action','Decisions/ablation/restart behavior: B20–B22; genuine provider: B23; B10 remains OPEN/PARTIAL']
STEPS={'BASELINE_VISIBLE':['Use returned case/asset/department IDs to request and schedule an inspection','Assigned department must start inspection; ADMIN release also requires its session and an independent ANALYST session'], 'EVIDENCE_REVEALED':['Inspect released evidence; independently investigate/assess alternatives','Draft a supported sourced plan and obtain exact approval through existing commands'], 'PLAN_AND_APPROVAL':['Create and assign authorized work through existing services','Complete only with independently reviewed evidence; then obtain a qualifying followup opportunity'], 'FOLLOW_UP':['Read actual outcome and monitoring records; stage is not verified resolution']}
class Demo:
 def __init__(self,s,token=None):self.s,self.token=s,token
 def state(self):return self.s.delivery.store.get('demo','current')
 def summary(self,state):
  return ScenarioSummary(id=state['id'],title='Demonstration '+state['id'],issue_types=[c['issue_type'] for c in state['cases']],stage=state['stage'],current_stage=state['stage'],cases=state['cases'],next_operator_steps=STEPS[state['stage']],limitations=LIMITATIONS).model_dump(mode='json')
 def catalog(self):
  # Delayed packet/catalog truth is never loaded by this read path.
  from .models import ScenarioID
  from typing import get_args
  from .inventory import ISSUES
  current=self.state();items=[]
  for id in get_args(ScenarioID):
   if current and current['id']==id:items.append(self.summary(current))
   else:items.append(ScenarioSummary(id=id,title='Demonstration '+id,issue_types=ISSUES[id],stage='NOT_STARTED',next_operator_steps=['ADMIN creates a fresh isolated run; retain existing source'],limitations=LIMITATIONS).model_dump(mode='json'))
  return ScenarioPage(items=items,next_cursor=None,total_count=len(items)).model_dump(mode='json')
 def prepare_reset(self,v,actor):
  if actor.role!='ADMIN':raise Denied('DEMO_ADMIN_REQUIRED')
  if not getattr(self.s,'_demo_memory_path',None):raise DemoBlocked('PRIVATE_DEMO_HOST_CONFIGURATION_REQUIRED')
  if timestamp(self.s.clock())<timestamp(BASE):raise DemoBlocked('DEMO_CLOCK_BEFORE_BASELINE')
  load() # Validate every definition before any new source writes.
 def reset(self,v,actor,request):
  from cli.reset import reset as fresh
  from cli.private import read_json
  # Fixed host-controlled parent and generated request identity: no path selector.
  parent=Path(self.s.profile_path).absolute().parent/'demo-runs'
  if parent.is_symlink():raise DemoBlocked('PRIVATE_DEMO_DIRECTORY_REQUIRED')
  parent.mkdir(mode=0o700,exist_ok=True)
  if parent.stat().st_mode&0o077:raise DemoBlocked('PRIVATE_DEMO_DIRECTORY_REQUIRED')
  directory=parent/request
  self.s._cli_memory_path=self.s._demo_memory_path
  receipt=fresh(self.s,directory,request,actor)
  p=load_profile(directory/'profile.json');world=load()[v['scenario_id']]
  with active_scope(p):
   repo=GraphRepository(self.s.repo.client,p.graph)
   bundle=json.loads((ROOT/'data/ingestion/city-v3.json').read_text())
   from app.ingestion.conversion import validate_bundle
   validate_bundle(bundle)
   ids={'DRAIN-100','DRAIN-101','ROAD-100','PIPE-100','WASTE-100','ROUTE-C03','SCH-C03','EVD-B04-IMPORT','EVD-ASSET-LIST'}
   edges=[e for e in bundle['relationships'] if (e['source_id'] in ids and e['type'] in {'LOCATED_AT','MAINTAINED_BY','COLLECTED_BY','HAS_SCHEDULE'})]
   ids|={e['target_id'] for e in edges}|{e['properties']['source_evidence_id'] for e in edges}
   nodes=[n for n in bundle['nodes'] if n['properties']['id'] in ids]
   for n in sorted(nodes,key=lambda n:(n['label']!='Evidence',n['properties']['id'])):
    old=repo._node_optional(n['properties']['id'])
    if old:
     if old.properties!=n['properties']:raise Conflict('DEMO_BASELINE_COLLISION')
    else:repo.create_node(n['label'],n['properties'])
   if world.id=='S08':edges=[e for e in edges if not(e['source_id']=='WASTE-100' and e['type']=='LOCATED_AT')]
   for e in edges:
    if not repo._edge_optional(e['properties']['id']):repo.create_relationship(e['type'],e['source_id'],e['target_id'],e['properties'])
   # Explicit new synthetic survey, never promote imported candidate relationships.
   if world.id in {'S01','S07','S10'}:
    from app.services.evidence.writer import common
    eid='B19-BASELINE-SURVEY'
    repo.create_node('Evidence',{**common(eid,BASE),'recorded_at':BASE,'observed_at':BASE,'evidence_type':'SYNTHETIC_TOPOLOGY_SURVEY','summary':'Synthetic surveyed flow connection; no obstruction or cause is asserted','source_kind':'SYNTHETIC','source_record_id':'B19-v1-flow-survey','basis':'OBSERVED','reliability':'VERIFIED'})
    repo.create_relationship('DRAINS_TO','DRAIN-100','DRAIN-101',{'id':'B19-SURVEY-FLOW','municipality_id':'demo-city','created_at':BASE,'valid_from':BASE,'source_evidence_id':eid,'association_status':'VERIFIED'})
   if world.id in {'S03','S04','S08'}:
    from app.services.evidence.writer import common
    eid='B19-CONTEXT-SURVEY'
    repo.create_node('Evidence',{**common(eid,BASE),'recorded_at':BASE,'observed_at':BASE,'evidence_type':'SYNTHETIC_CONTEXT_SURVEY','summary':'Synthetic spatial/physical inventory context only; proximity is not causation','source_kind':'SYNTHETIC','source_record_id':'B19-v1-context-survey','basis':'OBSERVED','reliability':'VERIFIED'})
    if world.id=='S08':
     repo.create_node('Location',{**common('B19-NEARBY',BASE),'name':'Synthetic nearby survey point','latitude':25.31268,'longitude':82.9615})
     repo.create_relationship('LOCATED_AT','WASTE-100','B19-NEARBY',{'id':'B19-NEARBY-LOCATION','municipality_id':'demo-city','created_at':BASE,'source_evidence_id':eid})
    else:
     repo.create_relationship('UNDERLIES','PIPE-100','ROAD-100',{'id':'B19-SURVEY-UNDERLIES','municipality_id':'demo-city','created_at':BASE,'valid_from':BASE,'source_evidence_id':eid,'association_status':'VERIFIED'})
   from app.services.complaints.service import ComplaintService
   from app.events.service import Delivery
   delivery=Delivery(repo,lambda:BASE);cases=[]
   for issue in world.issues:
    out=ComplaintService(repo,clock=lambda:BASE).intake(intake(world,issue))
    # Repeated identical source record is established B08 idempotent intake, not a new episode.
    again=ComplaintService(repo,clock=lambda:BASE).intake(intake(world,issue))
    if again.complaint_id!=out.complaint_id:raise Conflict('DEMO_INTAKE_REPLAY')
    opened=EvidenceService(repo,clock=lambda:BASE).execute({'operation':'open','request_id':__import__('app.services.http.service',fromlist=['request_identity']).request_identity(p.graph,actor.id,'B19-baseline-'+world.id+'-'+issue),'incident_ids':[out.incident_id],'cluster_id':out.cluster_id},actor)
    asset,_,department=target(world,issue)
    cases.append(ScenarioCase(issue_type=issue,investigation_id=opened.entity_id,incident_id=out.incident_id,cluster_id=out.cluster_id,asset_id=asset,department_id=department).model_dump(mode='json'))
   # Only released/public state stored in runtime graph; no packet/expected decision.
   state={'id':world.id,'stage':'BASELINE_VISIBLE','cases':cases,'baseline_at':BASE}
   with repo._session() as session:delivery.store.write(session,[('demo','current',state)])
   # Variant is host-only; never put future packets/variant into canonical graphs.
   from cli.private import write_private
   write_private(directory/'world.json',{'version':1,'scenario_id':world.id,'variant':v['variant'],'source_graph':p.graph})
   hashes={n['properties']['id']:repo.get_node(n['properties']['id']).content_hash for n in nodes}
   hashes.update({e['properties']['id']:repo.get_relationship(e['properties']['id']).content_hash for e in edges})
   fingerprint=digest({'seed':v['seed'],'physical_records':hashes,'baseline_reports':[intake(world,i) for i in world.issues],'surveyed_flow':world.id in {'S01','S07','S10'},'context_survey':world.id if world.id in {'S03','S04','S08'} else None})
   counts={'nodes':repo._read('MATCH (n:CivicEntity) RETURN count(n)')[0][0],'relationships':repo._read('MATCH (:CivicEntity)-[r]->(:CivicEntity) RETURN count(r)')[0][0],'source_documents':repo._read('MATCH (n:Document) RETURN count(n)')[0][0],'seed_fingerprint':fingerprint}
   return {**counts,'scenario':self.summary(state),'source_graph':p.graph,'profile_reference':'demo-runs/'+request,'baseline_content_hash':fingerprint,'previous_source_preserved':True,'simulated':True}
 async def prepare_advance(self,id,v,actor,field,reviewer):
  if actor.role!='ADMIN':raise Denied('DEMO_ADMIN_REQUIRED')
  state=self.state()
  if not state or state['id']!=id or state['stage']!=v['expected_current_stage']:raise DemoBlocked('DEMO_STAGE_OR_SOURCE_MISMATCH')
  if timestamp(self.s.clock())<timestamp(state['baseline_at']):raise DemoBlocked('DEMO_CLOCK_BEFORE_BASELINE')
  expected={'BASELINE_VISIBLE':'EVIDENCE_REVEALED','EVIDENCE_REVEALED':'PLAN_AND_APPROVAL','PLAN_AND_APPROVAL':'FOLLOW_UP'}
  if expected.get(state['stage'])!=v['stage']:raise DemoBlocked('DEMO_STAGE_ORDER')
  if v['stage']=='EVIDENCE_REVEALED':
   if not field or field.role!='DEPARTMENT_LEAD' or not reviewer or reviewer.role!='ANALYST' or field.id==reviewer.id:raise Denied('DEMO_FIELD_AND_REVIEWER_REQUIRED')
   case=next((c for c in state['cases'] if c['investigation_id']==v['investigation_id']),None)
   if not case or case['evidence_ids']:raise DemoBlocked('DEMO_CASE_ALREADY_RELEASED_OR_UNBOUND')
   if field.department_id!=case['department_id']:raise Denied('DEMO_FIELD_DEPARTMENT')
   if not v['inspection_id'] or not v['expected_hash']:raise DemoBlocked('DEMO_ACTIVE_INSPECTION_REQUIRED')
   ins=self.s.repo.get_node(v['inspection_id'],'Inspection')
   if ins.content_hash!=v['expected_hash']:raise Conflict('DEMO_STALE_INSPECTION')
   source,assets=EvidenceService(self.s.repo).inspection_source(Reader(self.s.repo,self.s.clock()),ins.id)
   if ins.properties['status']!='IN_PROGRESS' or source['investigation_id']!=case['investigation_id'] or source['department_id']!=case['department_id'] or assets!={case['asset_id']}:raise DemoBlocked('DEMO_INSPECTION_BINDING_LIFECYCLE')
   if timestamp(ins.properties['updated_at'])>timestamp(self.s.clock()):raise DemoBlocked('DEMO_OBSERVATION_BEFORE_INSPECTION')
   return state,case,None
  # Later stages only observe accepted operational prerequisites, never enact them.
  if not v['plan_id']:raise DemoBlocked('DEMO_APPROVED_PLAN_REQUIRED')
  plan=self.s.ops.planning.store.get(v['plan_id'])
  if not plan or plan['draft']['investigation_id'] not in {c['investigation_id'] for c in state['cases']}:raise DemoBlocked('DEMO_PLAN_SCOPE')
  approvals=self.s.reads.ids('Approval')
  approved=False;approved_binding=None;approved_state=None
  for aid in approvals:
   binding=self.s.ops.store.get('approval',aid)
   if binding and binding['binding']['plan_id']==v['plan_id']:
    a,_=self.s.ops.approval(aid,binding['binding'])
    if a.properties['status']=='APPROVED' and binding['binding']['plan_hash']==plan['receipt']['plan_hash']:approved=True;approved_binding=binding['binding'];approved_state=binding
  if not approved:raise DemoBlocked('DEMO_EXACT_APPROVAL_REQUIRED')
  await self.s.ops.validate(approved_binding,self.s.clock(),progress=v['stage']=='FOLLOW_UP')
  if v['stage']=='FOLLOW_UP':
   if not v['work_order_id']:raise DemoBlocked('DEMO_COMPLETED_WORK_REQUIRED')
   w,order=self.s.ops.verified_order(v['work_order_id'])
   if order['binding']['plan_id']!=v['plan_id'] or w.properties.get('status')!='COMPLETED':raise DemoBlocked('DEMO_COMPLETED_WORK_SCOPE')
   # Do not invent a qualifying opportunity. Existing outcome monitor supplies it.
   result=self.s.reads.get(w.id,'WorkOrder',actor,self.token)
   if not result.get('resolution_verified'):raise DemoBlocked('DEMO_QUALIFYING_INDEPENDENT_OUTCOME_REQUIRED')
  if v['stage']=='FOLLOW_UP':
   verification=self.s.ops.store.get('verification',w.id)
   record=self.s.ops.store.get('outcome',verification['outcome_id'])
   operation=self.s.ops.store.get('operation',record['last_operation']);typ='INTERVENTION_OUTCOME_RECORDED'
  else:operation=self.s.ops.store.get('operation',approved_state['last_operation']);typ='PLAN_APPROVED'
  events=[e for e in operation['events'] if e['type']==typ]
  if len(events)!=1:raise DemoBlocked('DEMO_PREREQUISITE_EVENT_REQUIRED')
  native=self.s.repo.get_node(events[0]['id'],'DomainEvent')
  checked=list(self.s.delivery.sources.events('native',native.id,native.properties))
  if len(checked)!=1 or checked[0].model_dump(mode='json')!=events[0]:raise DemoBlocked('DEMO_PREREQUISITE_EVENT_REQUIRED')
  case=next(c for c in state['cases'] if c['investigation_id']==plan['draft']['investigation_id'])
  return state,case,native.id
 def advance(self,id,v,actor,field,reviewer,request,prepared):
  state,case,event_id=prepared;store=self.s.delivery.store
  if v['stage']=='EVIDENCE_REVEALED':
   reservation='release:'+id+':'+case['investigation_id']
   with self.s.repo._session() as session:
    if store.get('demo_release',reservation):raise Recovery(request,identities={'investigation_id':case['investigation_id'],'entity_id':v['inspection_id']})
    store.write(session,[('demo_release',reservation,{'request_id':request,'status':'DISPATCHING'})])
   from cli.private import read_json
   private=read_json(Path(self.s.profile_path).parent/'world.json',private=True)
   if private!={'version':1,'scenario_id':id,'variant':private.get('variant'),'source_graph':self.s.profile.graph} or private['variant'] not in {'PRIMARY','NEGATIVE'}:raise Recovery(request)
   world=load()[id];samples=(world.release if private['variant']=='PRIMARY' else world.negative)[case['issue_type']]
   observations=[{'asset_id':case['asset_id'],'method':'SYNTHETIC_FIELD_SURVEY','observed_at':self.s.clock(),**x.model_dump(mode='json')} for x in samples]
   report=EvidenceService(self.s.repo,clock=self.s.clock).execute({'operation':'report_inspection','request_id':request,'inspection_id':v['inspection_id'],'expected_hash':v['expected_hash'],'source_id':'B19-field','record_id':id+':'+case['investigation_id'],'source_kind':'SYNTHETIC','observations':observations,'review':Review(reviewer_id=reviewer.id,role='ANALYST',reviewed=True,reason='Independent authenticated review of controlled synthetic world observations').model_dump(mode='json'),'attribution':{'incident_ids':[case['incident_id']],'mode':'OCCURRENCE','rationale':'Direct synthetic field observation for this active episode','basis_evidence_ids':[]}},field)
   service_source=None
   if id in {'S05','S06'}:
    from .service_history import release
    service_source=release(self.s,id,private['variant'],case,report.entity_id,field,reviewer,request)
   journal=self.s.repo.get_node(report.journal_id,'Evidence')
   events=list(self.s.delivery.sources.events('journal',journal.id,journal.properties))
   if len(events)!=1:raise Recovery(request)
   event_id=events[0].id
   self.s.delivery.register(events[0],'journal:'+journal.id)
   with self.s.repo._session() as session:
    current=store.get('demo','current')
    target=next(c for c in current['cases'] if c['investigation_id']==case['investigation_id']);target['evidence_ids']=[report.entity_id]+([service_source['id']] if service_source else [])
    advanced=all(c['evidence_ids'] for c in current['cases'])
    if advanced:current['stage']='EVIDENCE_REVEALED'
    store.write(session,[('demo','current',current),('demo_release',reservation,{'request_id':request,'status':'DONE','evidence_id':report.entity_id})])
   return {'scenario_id':id,'stage':current['stage'],'event_id':event_id,'revealed_evidence_ids':target['evidence_ids'],'scenario':self.summary(current),'released_evidence_ids':target['evidence_ids'],'stage_advanced':advanced,'simulated':True}
  with self.s.repo._session() as session:
   current=store.get('demo','current')
   target=next(c for c in current['cases'] if c['investigation_id']==case['investigation_id'])
   field='plan_id' if v['stage']=='PLAN_AND_APPROVAL' else 'work_order_id'
   target[field]=v[field]
   advanced=all(c.get(field) for c in current['cases'])
   if advanced:current['stage']=v['stage']
   store.write(session,[('demo','current',current)])
  return {'scenario_id':id,'stage':current['stage'],'event_id':event_id,'revealed_evidence_ids':[],'scenario':self.summary(current),'released_evidence_ids':[],'stage_advanced':advanced,'simulated':True}
