"""One clean retained waste case: staged operator-assisted lifecycle.

Preparation submits a non-executable draft. Execution requires its human-approved
hash and retains monitoring. No model wake, clock change or recovery reset.
The explicit pre-intent recovery flag permits one proven same-key attempt only.
Every mutation gets an exclusive dispatch marker before the authenticated request.
"""
import argparse,json,os
from datetime import timedelta
from pathlib import Path
from exact_road_lifecycle import Journey
from app.graph.schema import utc_now

CASE='INV-B09-95e00a75e74b708c966db68bc595dca0'
INCIDENT='INC-B08-1cca3446575fbdc579f88488fafa601b'
REPORT='EV-REPORT-B09-4b525fd118ca5c3b54318eb492027c83'
TARGET='WASTE-DEMO-SERVICE-02'
EVIDENCE=Path('docs/evidence/DEMO-WASTE-COMPLETION')
PRIVATE=Path('.runtime/demo-presenter/run-01/waste-completion')

def write_new(path,value,private=False):
 path.parent.mkdir(parents=True,exist_ok=True,mode=0o700 if private else 0o755)
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600 if private else 0o644)
 with os.fdopen(fd,'w') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())

class WastePreparation(Journey):
 def __init__(self,retry_proven_unstarted=False):
  super().__init__();self.retry_proven_unstarted=retry_proven_unstarted
 def proven_unstarted(self,marker,key,path,who):
  if not self.retry_proven_unstarted or key!='assess-capacity_shortfall' or who!='OP-ANALYST':raise RuntimeError('PRIOR_DISPATCH_REQUIRES_REVIEW')
  from app.config import Settings
  from app.graph.connection import connect
  from app.graph.repository import GraphRepository
  from app.active import load,active_scope
  from app.events.store import Store
  from app.services.http.service import request_identity
  from app.services.evidence.writer import stable
  from app.graph.models import digest
  original=json.loads(marker.read_text());profile=load(self.config.profile)
  if original['path']!=path or original['actor']!=who or original['key']!='EXACT-ROAD-WASTE-COMPLETION-'+key:raise RuntimeError('ORIGINAL_REQUEST_MISMATCH')
  request=request_identity(profile.graph,who,original['key'])
  with connect(Settings(_env_file='.env')) as db,active_scope(profile):
   repo=GraphRepository(db,profile.graph);state=repo._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.repo_revision,coalesce(m.repo_pending,'')")
   if state!=[[1056,'']] or Store(repo,utc_now).get('api_request',request) is not None or repo._node_optional(stable('EV-JOURNAL',who,request)) is not None:raise RuntimeError('NO_DISPATCH_NOT_PROVEN')
   if repo.get_node(path.split('/')[2],'Hypothesis').content_hash!=original['body']['expected_hash']:raise RuntimeError('ORIGINAL_SOURCE_CHANGED')
  retry=marker.with_name(key+'-manual-proven-prewrite-dispatch.json')
  write_new(EVIDENCE/'manual-prewrite-reconciliation.json',{'at':utc_now(),'request_id':request,'original_dispatch_hash':digest(original),'repository':state,'intent':None,'domain_journal':None,'original_hypothesis_unchanged':True,'action':'ONE_EXPLICIT_SAME_KEY_SAME_PAYLOAD_ATTEMPT_AFTER_LOCAL_API_RELOAD'})
  return retry,original['body']
 def call(self,method,path,body=None,who='OP-ANALYST',key=None,review=False):
  marker=None
  if method!='GET':
   if not key:raise RuntimeError('EXPLICIT_REQUEST_KEY_REQUIRED')
   marker=PRIVATE/(key+'-dispatch.json')
   if marker.exists():marker,body=self.proven_unstarted(marker,key,path,who)
   write_new(marker,{'at':utc_now(),'method':method,'path':path,'actor':who,'body':body,'key':'EXACT-ROAD-WASTE-COMPLETION-'+key},True)
  result=super().call(method,path,body,who,'WASTE-COMPLETION-'+key if key else None,review)
  if marker:write_new(marker.with_name(marker.stem+'-receipt.json'),result,True)
  return result
 def prepare(self):
  inv=self.call('GET','/investigations/'+CASE);trace=self.call('GET','/investigations/'+CASE+'/trace')
  if inv['status']!='OPEN' or trace['recovery_required'] or trace['pause_reason']!='TOKEN_BUDGET' or inv.get('current_plan_id'):raise RuntimeError('CLEAN_OPEN_USAGE_PAUSED_CASE_REQUIRED')
  if self.call('GET','/investigations/'+CASE+'/plans')['items']:raise RuntimeError('EXISTING_PLAN_REVIEW_REQUIRED')
  source=self.call('GET','/evidence/'+REPORT)
  if not source['reviewed'] or source['source_kind']!='SYNTHETIC' or INCIDENT not in source['observation_source']['attribution']['incident_ids']:raise RuntimeError('REVIEWED_ATTRIBUTED_SOURCE_REQUIRED')
  if self.call('GET','/assets/'+TARGET)['owner_department_id']!='DEPT-SAN':raise RuntimeError('OWNERSHIP_REQUIRED')
  before=self.call('GET','/investigations/'+CASE+'/hypotheses')['items']
  if {h['cause_code'] for h in before}!={'MISSED_PICKUP','CAPACITY_SHORTFALL'}:raise RuntimeError('EXACT_EXISTING_HYPOTHESES_REQUIRED')
  for h in before:
   self.call('POST','/hypotheses/'+h['id']+'/assessments',{'expected_hash':h['expected_hash'],'evidence_ids':[REPORT],'as_of':utc_now()},key='assess-'+h['cause_code'].lower())
  hs=self.call('GET','/investigations/'+CASE+'/hypotheses')['items'];pickup=next(h for h in hs if h['cause_code']=='MISSED_PICKUP')
  if pickup['status'] not in {'SUPPORTED','VERIFIED'} or REPORT not in pickup['supporting_evidence_ids']:raise RuntimeError('REVIEWED_PICKUP_SUPPORT_REQUIRED')
  procedures=self.call('GET','/procedures?limit=50')['items'];procedure=next(p for p in procedures if p['id']=='ORG:D021:1');citation=next(c for c in procedure['citations'] if c['source_document_id']=='D021')
  refs=[REPORT]
  task={'id':'recover-missed-pickup','action_type':'MISSED_PICKUP_RECOVERY','target_ids':[TARGET],'department_id':'DEPT-SAN','priority':'HIGH','prerequisites':['Exact human approval, current verified responsibility and reviewed causal/safety observations'],'depends_on':[],'evidence_ids':refs,'assessment_ids':[pickup['current_assessment_id']],'procedure_citation':citation,'expected_outcome':'Recover the reviewed missed collection at this synthetic collection point; this does not resolve any unproven capacity issue','verification_criteria':'Independent reviewed completion followed by scheduled/actual pickups and at least24hours after pickup with a dated reaccumulation observation','risks':['Synthetic proposed guidance, not approved municipal policy','A missed-pickup recovery does not prove that capacity is adequate'],'remediation':{'mode':'SUPPORTED_NOW','conditions':[{'kind':kind,'status':'MET','evidence_ids':refs} for kind in ['CAUSAL_INSPECTION','SAFETY_REVIEW']]}}
  draft={'investigation_id':CASE,'issue':'WASTE_ACCUMULATION','version':1,'basis':[{'hypothesis_id':h['id'],'assessment_id':h['current_assessment_id'],'reason':'Reviewed missed-pickup and persistent-waste observations support bounded pickup recovery; this is an operator-assisted proposal.' if h['id']==pickup['id'] else 'Capacity remains a separate unresolved explanation. Overflow after missed service does not establish sustained capacity failure or authorize capacity changes.','addressed':h['id']==pickup['id']} for h in hs],'evidence_ids':refs,'tasks':[task],'expected_outcomes':['Recover the missed collection, then independently observe whether waste reaccumulates under scheduled service'],'risks':['Simulated work and field observations only; no actual municipal dispatch'],'uncertainties':['The original genuine AI run reached its token budget before reassessment; this reassessment and draft are operator-assisted','Both capacity and missed-service explanations retain their recorded assessment and missing evidence','No post-work24hour observation window has occurred; completion must not be presented as resolution'],'monitoring':{'issue':'WASTE_ACCUMULATION','required_evidence':['SCHEDULED_PICKUPS','ACTUAL_PICKUPS','REACCUMULATION_WINDOW'],'observation_opportunity':'Actual elapsed minimum24hour post-pickup window in the synthetic demo timeline, with independent dated scheduled/actual pickup and reaccumulation observations','verification_criteria':'All required scheduled pickups completed and no reaccumulation over at least24hours after the actual pickup; absent opportunity remains unresolved'}}
  plan=self.call('POST','/plans',{'draft':draft},key='draft-v1')
  assignments=[]
  for t in plan['task_bindings']:
   if t['eligible_assignee_ids']!=['OP-WASTE-LEAD']:raise RuntimeError('EXACT_ELIGIBLE_WASTE_LEAD_REQUIRED')
   assignments.append({k:t[k] for k in ['task_id','action_type','target_ids','department_id']}|{'assignee_id':'OP-WASTE-LEAD'})
  binding={'plan_id':plan['plan_id'],'plan_version':plan['version'],'plan_hash':plan['content_hash'],'assignments':assignments}
  approval=self.call('POST','/plans/'+plan['plan_id']+'/submit-approval',{k:v for k,v in binding.items() if k!='plan_id'},key='submit-v1')
  result={'mode':'AUTHENTICATED_OPERATOR_ASSISTED_NO_MODEL_OR_WORK_EXECUTION','case':CASE,'incident':INCIDENT,'source_report':REPORT,'before_hypotheses':before,'after_hypotheses':hs,'plan':plan,'binding':binding,'approval':approval,'human_approved':False,'work_executed':False,'calls':self.calls}
  write_new(EVIDENCE/'review.json',result)
  print(json.dumps({'plan_id':binding['plan_id'],'version':binding['plan_version'],'hash':binding['plan_hash'],'approval_id':approval['id'],'assignments':assignments,'work_executed':False},indent=2))
 def execute(self,approved_hash):
  from app.graph.schema import timestamp
  review=json.loads((EVIDENCE/'review.json').read_text());binding=review['binding']
  if not approved_hash or approved_hash!=binding['plan_hash']:raise RuntimeError('EXACT_HUMAN_APPROVED_HASH_REQUIRED')
  plan=self.call('GET','/plans/'+binding['plan_id'])
  if plan['content_hash']!=approved_hash or plan['status']!='PENDING_APPROVAL':raise RuntimeError('EXACT_PENDING_PLAN_REQUIRED')
  assignment=binding['assignments'][0];who=assignment['assignee_id']
  if len(binding['assignments'])!=1 or (who,assignment['action_type'],assignment['target_ids'])!=('OP-WASTE-LEAD','MISSED_PICKUP_RECOVERY',[TARGET]):raise RuntimeError('EXACT_WASTE_SCOPE_REQUIRED')
  approval=self.call('GET','/approvals/'+review['approval']['id'],who='OP-APPROVER')
  decision=self.call('POST','/approvals/'+approval['id']+'/decision',{**binding,'expected_hash':approval['expected_hash'],'decision':'APPROVED','reason':'Explicit human approval of this exact simulated missed-pickup recovery, scope and assignee; independent follow-up still required'},who='OP-APPROVER',key='approve-v1')
  work=self.call('POST','/work-orders',{**binding,'approval_id':approval['id'],'task_id':assignment['task_id']},who='OP-APPROVER',key='work-v1');wid=work['id']
  def current():return self.call('GET','/work-orders/'+wid)
  self.call('POST','/work-orders/'+wid+'/status',{'expected_hash':current()['expected_hash'],'new_status':'ASSIGNED','reason':'Assign the exact human-approved synthetic pickup recovery'},who=who,key='assign')
  self.call('POST','/work-orders/'+wid+'/progress',{'expected_hash':current()['expected_hash'],'action':'START','reason':'Begin explicitly simulated collection after current authority checks','evidence_ids':[]},who=who,key='start')
  def report(purpose,codes):
   def command(value,step,reviewed=False):
    body={'expected_hash':current()['expected_hash'],'purpose':purpose,'command':value}
    if reviewed:body['review_reason']='Independent analyst review of explicitly synthetic dated pickup observations; no real municipal work claimed'
    return self.call('POST','/work-orders/'+wid+'/inspections',body,who=who,key=purpose.lower()+'-'+step,review=reviewed)['status']
   iid=command({'operation':'request_inspection','investigation_id':CASE,'asset_ids':[TARGET],'department_id':'DEPT-SAN','inspection_type':'B14_FOLLOWUP' if purpose=='FOLLOWUP' else 'MISSED_PICKUP_RECOVERY'},'request')
   for status in ['REQUESTED','SCHEDULED','IN_PROGRESS']:
    inspection=self.call('GET','/inspections/'+iid);value={'operation':'transition_inspection','inspection_id':iid,'expected_hash':inspection['expected_hash'],'status':status}
    if status=='SCHEDULED':value['scheduled_at']=utc_now()
    command(value,status.lower())
   inspection=self.call('GET','/inspections/'+iid);at=utc_now()
   observations=[{'asset_id':TARGET,'code':code,'statement':'Explicit synthetic demo: '+('the missed collection was recovered' if code=='ACTION_COMPLETED' else 'one scheduled collection and one actual pickup are recorded at this time; later reaccumulation is not yet observed'),'method':'DIRECT_SYNTHETIC_FIELD_TEST','observed_at':at,'result':'OBSERVED','value':1.0 if code in {'SCHEDULED_PICKUPS','ACTUAL_PICKUPS'} else None,'unit':'pickups' if code in {'SCHEDULED_PICKUPS','ACTUAL_PICKUPS'} else None} for code in codes]
   rid=command({'operation':'report_inspection','inspection_id':iid,'expected_hash':inspection['expected_hash'],'source_id':'WASTE-COMPLETION-'+purpose,'record_id':iid,'source_kind':'SYNTHETIC','observations':observations},'report',True)
   return {'inspection_id':iid,'evidence_id':rid,'observed_at':at}
  completion=report('COMPLETION',['ACTION_COMPLETED'])
  self.call('POST','/work-orders/'+wid+'/progress',{'expected_hash':current()['expected_hash'],'action':'COMPLETE','reason':'Independently reviewed synthetic pickup completion; required elapsed follow-up remains outstanding','evidence_ids':[completion['evidence_id']]},who=who,key='complete')
  start=utc_now();pickup=report('FOLLOWUP',['SCHEDULED_PICKUPS','ACTUAL_PICKUPS']);end=utc_now()
  outcome=self.call('POST','/work-orders/'+wid+'/outcomes',{'expected_hash':current()['expected_hash'],'evidence_ids':[pickup['evidence_id']],'window_start':start,'window_end':end},key='initial-monitoring')
  if outcome['assessment_status']=='RESOLUTION_VERIFIED':raise RuntimeError('PREMATURE_RESOLUTION_MUST_NOT_PASS')
  result={'mode':'HUMAN_APPROVED_OPERATOR_SIMULATION_NO_PROVIDER','binding':binding,'approval':decision,'work_order':current(),'completion':completion,'pickup':pickup,'outcome':outcome,'earliest_post_pickup_followup':(timestamp(pickup['observed_at'])+timedelta(hours=24)).isoformat(),'plan':self.call('GET','/plans/'+binding['plan_id']),'investigation':self.call('GET','/investigations/'+CASE),'incident':self.call('GET','/incidents/'+INCIDENT),'calls':self.calls}
  if result['plan']['status']!='MONITORING' or result['investigation']['status']=='COMPLETED' or result['incident']['status']=='ENDED':raise RuntimeError('MONITORING_MUST_RETAIN_OPEN_CASE')
  write_new(EVIDENCE/'execution.json',result);print(json.dumps({'work_order_id':wid,'status':result['work_order']['status'],'plan_status':result['plan']['status'],'earliest_followup':result['earliest_post_pickup_followup'],'case_closed':False}))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('command',choices=['prepare','execute']);parser.add_argument('--retry-proven-unstarted',action='store_true');parser.add_argument('--approve-plan-hash');args=parser.parse_args()
 j=WastePreparation(args.retry_proven_unstarted)
 try:
  if args.command=='prepare':j.prepare()
  else:j.execute(args.approve_plan_hash)
 finally:j.close()
