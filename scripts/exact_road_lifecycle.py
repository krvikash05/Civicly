"""Staged operator-assisted lifecycle for the human-selected original road incident.
Preparation submits a non-executable draft. Execution requires the exact human-approved
hash. All observations are explicitly synthetic; all writes use authenticated HTTP.
No provider wake, checkpoint rewrite, quarantine clearing, or budget modification.
"""
import argparse,asyncio,json
from pathlib import Path
import httpx
from app.demo_host.config import load
from app.active import load as profile_load,active_scope
from app.memory.runtime import configured
from app.graph.schema import utc_now
from cli.private import read_json
CASE='INV-B09-b9d4d66e130ed348c4f6a50e9d66a891'
INCIDENT='INC-B08-27a2cb5d89ae9ab9d86f999cf7b50472'
ROOT=Path('.runtime/demo-presenter/run-01')
PROOF=Path('docs/evidence/EXACT-ROAD-LIFECYCLE')

class Journey:
 def __init__(self):
  self.config=load(ROOT/'host.json');self.passwords=read_json(ROOT/'presenter-credentials.json',private=True)
  self.c=httpx.Client(base_url='http://127.0.0.1:8010/api/v1',timeout=120);self.tokens={};self.calls=[]
 def token(self,who):
  if who not in self.tokens:
   r=self.c.post('/auth/demo-login',json={'operator_id':who,'demo_password':self.passwords[who]});r.raise_for_status();self.tokens[who]=r.json()['data']['access_token']
  return self.tokens[who]
 def call(self,method,path,body=None,who='OP-ANALYST',key=None,review=False):
  h={'Authorization':'Bearer '+self.token(who)}
  if key:h['Idempotency-Key']='EXACT-ROAD-'+key
  if review:h['X-Reviewer-Authorization']='Bearer '+self.token('OP-ANALYST')
  r=self.c.request(method,path,json=body,headers=h);out=r.json()
  self.calls.append({'method':method,'path':path,'operator':who,'key':key,'http':r.status_code})
  if r.status_code!=200:raise RuntimeError(json.dumps({'path':path,'http':r.status_code,'response':out}))
  return out['data']
 def close(self):
  for t in self.tokens.values():self.c.post('/auth/logout',json={},headers={'Authorization':'Bearer '+t})
  self.c.close()
 def save(self,suffix,value):
  path=Path(str(PROOF)+'-'+suffix+'.json')
  if path.exists():raise RuntimeError('IMMUTABLE_PROOF_ALREADY_EXISTS')
  path.write_text(json.dumps(value,indent=2)+'\n')
 async def prepare(self):
  # Preserve uncertainty about additional extent, rather than asserting that the
  # two observed mechanisms exhaust every possible cause or affected segment.
  alt=self.call('POST','/investigations/'+CASE+'/hypotheses',{'incident_ids':[INCIDENT],'asset_ids':['ROAD-100'],'cause_code':'SUBGRADE_FAILURE','statement':'Additional independently unsupported extent of subgrade damage beyond the inspected repair footprint remains uncertain.','mechanism':'The two existing reviewed inspections support bounded work, but do not establish the extent of any additional damage. Do not authorize extra work from this alternative.','confirming_codes':['SUBGRADE_FAILURE_OBSERVED','STRUCTURAL_TEST_FAILED'],'falsifying_codes':['SUBGRADE_TEST_NORMAL']},key='retained-extent-alternative')['status']
  hypothesis=self.call('GET','/hypotheses/'+alt)
  if not hypothesis['current_assessment_id']:self.call('POST','/hypotheses/'+alt+'/assessments',{'expected_hash':hypothesis['expected_hash'],'evidence_ids':[],'as_of':utc_now()},key='extent-inconclusive')
  hs=self.call('GET','/investigations/'+CASE+'/hypotheses')['items'];by={h['id']:h for h in hs}
  utility=by['HYP-B09-141618e9674e96533d1d680ab206832c'];road=by['HYP-B09-a15ee19ac01f02a6b6a3622d8f08df5d']
  p=profile_load(self.config.profile)
  with active_scope(p):db,memory=configured(p.graph,self.config.memory_profile).connect()
  try:
   with active_scope(p):
    citations={doc:(await memory.retrieve(as_of=utc_now(),document_id=doc))['citations'][0] for doc in ['D020','D022']}
  finally:db.connection.close();db.connection.connection_pool.disconnect()
  basis=[{'hypothesis_id':h['id'],'assessment_id':h['current_assessment_id'],'reason':'Reviewed bounded mechanism supports conditional simulated remedy' if h['id']!=alt else 'Retained uncertain extent does not authorize additional work','addressed':h['id']!=alt} for h in hs]
  evidence=sorted(set(utility['supporting_evidence_ids']+road['supporting_evidence_ids']))
  tasks=[]
  for id,action,target,dept,h,doc,dep,guard in [('isolate','UTILITY_ISOLATION','PIPE-100','DEPT-WATER',utility,'D022',None,None),('repair','UTILITY_LEAK_REPAIR','PIPE-100','DEPT-WATER',utility,'D022','isolate','ISOLATION_PROOF'),('road','SUBGRADE_REPAIR','ROAD-100','DEPT-ROAD',road,'D020','repair','UTILITY_VERIFICATION')]:
   refs=h['supporting_evidence_ids'];conditions=[{'kind':k,'status':'MET','evidence_ids':refs} for k in ['CAUSAL_INSPECTION','SAFETY_REVIEW']]
   if guard:conditions.append({'kind':guard,'status':'UNMET','depends_on_task_id':dep})
   tasks.append({'id':id,'action_type':action,'target_ids':[target],'department_id':dept,'priority':'HIGH','prerequisites':['Exact human approval and independently reviewed synthetic field evidence required'],'depends_on':[dep] if dep else [],'evidence_ids':refs,'assessment_ids':[h['current_assessment_id']],'procedure_citation':citations[doc],'expected_outcome':'Bounded simulated '+action+'; completion alone does not establish case resolution','verification_criteria':'Independent reviewed post-work evidence and all typed dependency gates','risks':['Synthetic proposed procedure; unknown extent outside inspected footprint'],'remediation':{'mode':'CONDITIONAL' if dep else 'SUPPORTED_NOW','conditions':conditions}})
  draft={'investigation_id':CASE,'issue':'ROAD_DAMAGE','version':1,'basis':basis,'evidence_ids':evidence,'tasks':tasks,'expected_outcomes':['Stop verified utility infiltration before repairing the inspected road footprint'],'risks':['This is an explicitly synthetic demo, not actual field execution'],'uncertainties':['Both causal assessments remain SUPPORTED, not independently VERIFIED; additional extent remains unresolved','Gemini reached its existing token budget; this draft is analyst-assisted, not an autonomous model recommendation'],'monitoring':{'issue':'ROAD_DAMAGE','required_evidence':['WEAR_EXPOSURE','FOLLOWUP_PAVEMENT'],'observation_opportunity':'Explicit simulated wear exposure and independently reviewed pavement follow-up after completed work','verification_criteria':'Utility repair independently verified first; no adverse pavement finding following synthetic wear; all work completed; absent opportunity remains unresolved'}}
  plan=self.call('POST','/plans',{'draft':draft},key='draft-v1')
  assignments=[{k:t[k] for k in ['task_id','action_type','target_ids','department_id']}|{'assignee_id':'OP-WATER-LEAD' if t['department_id']=='DEPT-WATER' else 'OP-ROAD-LEAD'} for t in plan['task_bindings']]
  binding={'plan_id':plan['plan_id'],'plan_version':plan['version'],'plan_hash':plan['content_hash'],'assignments':assignments}
  approval=self.call('POST','/plans/'+plan['plan_id']+'/submit-approval',{k:v for k,v in binding.items() if k!='plan_id'},key='submit-v1')
  self.save('review',{'mode':'ANALYST_ASSISTED_DRAFT_AFTER_REAL_GEMINI_ASSESSMENT','case':CASE,'incident':INCIDENT,'plan':plan,'binding':binding,'approval':approval,'calls':self.calls,'human_approval_obtained':False,'work_execution_performed':False})
  print(json.dumps({'plan_id':plan['plan_id'],'version':plan['version'],'hash':plan['content_hash'],'approval_id':approval['id'],'tasks':assignments},indent=2))

 def execute(self,approved_hash):
  from cli.private import write_private
  review=json.loads(Path(str(PROOF)+'-review.json').read_text());b=review['binding']
  if approved_hash!=b['plan_hash']:raise RuntimeError('EXACT_HUMAN_APPROVED_HASH_REQUIRED')
  plan=self.call('GET','/plans/'+b['plan_id'])
  if plan['content_hash']!=approved_hash or plan['status']!='PENDING_APPROVAL':raise RuntimeError('PLAN_CHANGED_OR_NOT_PENDING')
  write_private(ROOT/'exact-road-execution-started.json',{'plan_id':b['plan_id'],'hash':approved_hash,'human_authorized':True,'at':utc_now(),'automatic_retry':False})
  a=self.call('GET','/approvals/'+review['approval']['id'],who='OP-APPROVER')
  decision=self.call('POST','/approvals/'+a['id']+'/decision',{**b,'expected_hash':a['expected_hash'],'decision':'APPROVED','reason':'Explicit human approval in Codex of this exact simulated plan, hash, tasks and assignees'},who='OP-APPROVER',key='approve-v1')
  results={'mode':'AUTHENTICATED_OPERATOR_SIMULATION_NOT_AUTONOMOUS_EXECUTION','human_approved_hash':approved_hash,'approval':decision,'tasks':[]}
  for action in ['UTILITY_ISOLATION','UTILITY_LEAK_REPAIR','SUBGRADE_REPAIR']:
   assignment=next(t for t in b['assignments'] if t['action_type']==action);who=assignment['assignee_id']
   w=self.call('POST','/work-orders',{**b,'approval_id':a['id'],'task_id':assignment['task_id']},who='OP-APPROVER',key=action+'-order')
   wid=w['id']
   def current():return self.call('GET','/work-orders/'+wid)
   self.call('POST','/work-orders/'+wid+'/status',{'expected_hash':current()['expected_hash'],'new_status':'ASSIGNED','reason':'Assign exact human-approved synthetic task'},who=who,key=action+'-assign')
   self.call('POST','/work-orders/'+wid+'/progress',{'expected_hash':current()['expected_hash'],'action':'START','reason':'Begin explicitly simulated task after prerequisite revalidation','evidence_ids':[]},who=who,key=action+'-start')
   def report(purpose,codes):
    def command(c,step,reviewed=False):
     body={'expected_hash':current()['expected_hash'],'purpose':purpose,'command':c}
     if reviewed:body['review_reason']='Independent analyst review of explicitly synthetic dated observations for exact approved work'
     return self.call('POST','/work-orders/'+wid+'/inspections',body,who=who,key=action+'-'+purpose+'-'+step,review=reviewed)['status']
    iid=command({'operation':'request_inspection','investigation_id':CASE,'asset_ids':assignment['target_ids'],'department_id':assignment['department_id'],'inspection_type':'B14_FOLLOWUP' if purpose=='FOLLOWUP' else action},'request')
    for status in ['REQUESTED','SCHEDULED','IN_PROGRESS']:
     inspection=self.call('GET','/inspections/'+iid)
     c={'operation':'transition_inspection','inspection_id':iid,'expected_hash':inspection['expected_hash'],'status':status}
     if status=='SCHEDULED':c['scheduled_at']=utc_now()
     command(c,status)
    inspection=self.call('GET','/inspections/'+iid);at=utc_now()
    observations=[{'asset_id':assignment['target_ids'][0],'code':code,'statement':'Explicit synthetic demo observation '+code+'; no actual municipal field work claimed','method':'DIRECT_SYNTHETIC_FIELD_TEST','observed_at':at,'result':'OBSERVED','value':0.0 if code=='FOLLOWUP_PAVEMENT' else None,'unit':'boolean' if code=='FOLLOWUP_PAVEMENT' else None} for code in codes]
    rid=command({'operation':'report_inspection','inspection_id':iid,'expected_hash':inspection['expected_hash'],'source_id':'EXACT-ROAD-'+action+'-'+purpose,'record_id':iid,'source_kind':'SYNTHETIC','observations':observations},'report',True)
    return {'inspection_id':iid,'evidence_id':rid,'observations':observations}
   codes=['ACTION_COMPLETED']+(['UTILITY_ISOLATION_CONFIRMED'] if action=='UTILITY_ISOLATION' else [])
   completion=report('COMPLETION',codes)
   completed=self.call('POST','/work-orders/'+wid+'/progress',{'expected_hash':current()['expected_hash'],'action':'COMPLETE','reason':'Reviewed synthetic completion; resolution requires separate independent follow-up','evidence_ids':[completion['evidence_id']]},who=who,key=action+'-complete')
   row={'assignment':assignment,'work_order_id':wid,'completion_report':completion,'completion':completed}
   if action!='UTILITY_ISOLATION':
    if action=='SUBGRADE_REPAIR':
     results['monitoring_before_final_followup']={'plan':self.call('GET','/plans/'+b['plan_id']),'investigation':self.call('GET','/investigations/'+CASE),'monitoring':self.call('GET','/monitoring')}
     self.save('monitoring',results['monitoring_before_final_followup'])
    start=utc_now();follow=report('FOLLOWUP',['POST_REPAIR_PRESSURE_NORMAL','POST_REPAIR_LEAK_ABSENT'] if action=='UTILITY_LEAK_REPAIR' else ['WEAR_EXPOSURE','FOLLOWUP_PAVEMENT']);end=utc_now()
    outcome=self.call('POST','/work-orders/'+wid+'/outcomes',{'expected_hash':current()['expected_hash'],'evidence_ids':[follow['evidence_id']],'window_start':start,'window_end':end},key=action+'-evaluate')
    required='UTILITY_VERIFIED' if action=='UTILITY_LEAK_REPAIR' else 'RESOLUTION_VERIFIED'
    if outcome['assessment_status']!=required:raise RuntimeError('INDEPENDENT_VERIFICATION_NOT_PASSED')
    row.update(followup_report=follow,outcome=outcome)
   results['tasks'].append(row)
  results['calls']=self.calls;self.save('execution',results)
  self.verify()
 def verify(self):
  review=json.loads(Path(str(PROOF)+'-review.json').read_text());pid=review['binding']['plan_id']
  out={'mode':'FRESH_HTTP_PERSISTED_READBACK_NO_PROVIDER','incident':self.call('GET','/incidents/'+INCIDENT),'investigation':self.call('GET','/investigations/'+CASE),'plan':self.call('GET','/plans/'+pid),'hypotheses':self.call('GET','/investigations/'+CASE+'/hypotheses'),'graph':self.call('GET','/investigations/'+CASE+'/graph?depth=4&include_candidates=true'),'trace':self.call('GET','/investigations/'+CASE+'/trace'),'memory':self.call('GET','/cases/'+INCIDENT+'/memory'),'monitoring':self.call('GET','/monitoring')}
  if out['plan']['status']!='COMPLETED' or out['incident']['status']!='ENDED' or out['investigation']['status']!='COMPLETED':raise RuntimeError('FULL_LIFECYCLE_NOT_COMPLETE')
  own=next((row for row in out['memory']['items'] if row['id']==INCIDENT),None)
  if not own or len(own['outcome_ids'])!=5 or len(own['evidence_ids'])!=5:raise RuntimeError('COMPLETED_EPISODE_MEMORY_NOT_READABLE')
  if len([n for n in out['graph']['nodes'] if n.get('kind')=='WorkOrder'])!=3:raise RuntimeError('THREE_WORK_ORDERS_NOT_VISIBLE')
  self.save('verified-'+utc_now().replace(':','').replace('.',''),out)
  print(json.dumps({'incident':INCIDENT,'status':out['incident']['status'],'plan_status':out['plan']['status'],'investigation_status':out['investigation']['status'],'memory_items':len(out['memory']['items']),'graph_nodes':len(out['graph'].get('nodes',[])),'provider_requests':0},indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('operation',choices=['prepare','execute','verify']);p.add_argument('--approve-plan-hash');args=p.parse_args();j=Journey()
 try:
  if args.operation=='prepare':asyncio.run(j.prepare())
  elif args.operation=='execute':j.execute(args.approve_plan_hash)
  else:j.verify()
 finally:j.close()
if __name__=='__main__':main()
