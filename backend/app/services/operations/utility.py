"""B20-R-UTILITY component proofs over existing fenced operation storage."""
from app.graph.repository import PreconditionFailed
from app.graph.schema import timestamp
from app.services.evidence.reader import Reader
from app.services.planning.utility import DYNAMIC
VERSION='B20R-UTILITY-1'
ISOLATION='UTILITY_ISOLATION_CONFIRMED'
FOLLOWUP={'POST_REPAIR_PRESSURE_NORMAL','POST_REPAIR_LEAK_ABSENT','POST_REPAIR_PRESSURE_ABNORMAL','POST_REPAIR_LEAK_PRESENT'}

def isolation_proof(refs,targets,started_at):
 covered=set()
 for ref in refs:
  report=ref.report
  if not report or not report.review or report.source_kind!='SYNTHETIC':raise PreconditionFailed('REVIEWED_ISOLATION_REQUIRED')
  for ob in report.observations:
   if ob.code==ISOLATION and ob.result=='OBSERVED' and timestamp(ob.observed_at)>=timestamp(started_at):covered.add(ob.asset_id)
 if covered!=set(targets):raise PreconditionFailed('REVIEWED_ISOLATION_REQUIRED')

def evaluate(targets,observations,start,end,completed_at,now):
 from .verification import validate_observation
 lo,hi,done,at=map(timestamp,[start,end,completed_at,now])
 if not done<lo<=hi<=at:raise PreconditionFailed('OUTCOME_WINDOW_ORDER')
 missing=[];contrary=False;conflict=False
 for target in targets:
  codes=set()
  for ob in observations:
   if ob.asset_id!=target:continue
   validate_observation(ob,FOLLOWUP)
   if not lo<=timestamp(ob.observed_at)<=hi:raise PreconditionFailed('OUTCOME_EVIDENCE_OUTSIDE_WINDOW')
   if ob.result=='OBSERVED':codes.add(ob.code)
   else:missing.append(target+': unknown '+ob.code)
  for good,bad in [('POST_REPAIR_PRESSURE_NORMAL','POST_REPAIR_PRESSURE_ABNORMAL'),('POST_REPAIR_LEAK_ABSENT','POST_REPAIR_LEAK_PRESENT')]:
   conflict |= good in codes and bad in codes
   contrary |= bad in codes
   if good not in codes and bad not in codes:missing.append(target+': missing '+good)
 if conflict:return 'INCONCLUSIVE',['Contradictory post-repair observations retained']+missing
 if contrary:return 'PROBLEM_PERSISTS',missing
 if missing:return 'MONITORING',missing
 return 'UTILITY_VERIFIED',[]

def fulfilled(ops,task,saved,at):
 """Revalidate exact bound predecessor and immutable report hashes at authority time."""
 from .service import stable
 result=set();reader=Reader(ops.repo,at)
 for c in task.remediation.conditions if task.remediation else []:
  if c.kind not in DYNAMIC:continue
  if c.status!='UNMET' or not c.depends_on_task_id:raise PreconditionFailed('UTILITY_DEPENDENCY_BINDING')
  native=saved['task_ids'][c.depends_on_task_id];wid=stable('WO',saved['receipt']['id'],native)
  w,bound=ops.verified_order(wid)
  if w.properties['status']!='COMPLETED' or bound['assignment']['task_id']!=native:raise PreconditionFailed('UTILITY_DEPENDENCY_NOT_COMPLETED')
  completion=ops.store.get('completion',wid)
  if not completion or completion['action']!='COMPLETE':raise PreconditionFailed('UTILITY_COMPLETION_PROOF_REQUIRED')
  origin=ops.store.get('operation',completion['last_operation'])
  if not origin or origin['command']['work_order_id']!=wid or origin['receipt']['status']!='COMPLETED':raise PreconditionFailed('UTILITY_COMPLETION_PROOF_REQUIRED')
  refs=[reader.evidence(id) for id in completion['evidence_ids']]
  for ref in refs:
   report=ref.report;auth=ops.store.get('inspection',report.inspection_id) if report else None
   if not auth or auth['work_order_id']!=wid or auth['purpose']!='COMPLETION' or auth['procedure']!=next(t['procedure_citation'] for t in saved['draft']['tasks'] if t['id']==c.depends_on_task_id) or report.inspector_id!=bound['assignment']['assignee_id']:raise PreconditionFailed('UTILITY_REPORT_BINDING')
  if c.kind=='ISOLATION_PROOF':
   isolation_proof(refs,bound['assignment']['target_ids'],w.properties['created_at'])
  else:
   verified=ops.store.get('verification',wid);out=ops.store.get('outcome',verified['outcome_id']) if verified else None
   if not out or out['assessment_status']!='UTILITY_VERIFIED' or out['work_order_id']!=wid or out['plan_id']!=saved['receipt']['id'] or out['policy_version']!=VERSION:raise PreconditionFailed('UTILITY_VERIFICATION_REQUIRED')
   follow=[]
   for old in out['evidence_references']:
    ref=reader.evidence(old['id']);report=ref.report;auth=ops.store.get('inspection',report.inspection_id) if report else None
    if ref.content_hash!=old['content_hash'] or ref.finding_hashes!=old['finding_hashes'] or not report or not report.review or not auth or auth['work_order_id']!=wid or auth['purpose']!='FOLLOWUP' or auth['procedure']!=next(t['procedure_citation'] for t in saved['draft']['tasks'] if t['id']==c.depends_on_task_id) or report.inspector_id!=bound['assignment']['assignee_id'] or ref.source_record_id in completion['source_records']:raise PreconditionFailed('UTILITY_VERIFICATION_CHANGED')
    follow.extend(report.observations)
   status,_=evaluate(bound['assignment']['target_ids'],follow,out['window']['start'],out['window']['end'],completion['at'],at)
   if status!='UTILITY_VERIFIED':raise PreconditionFailed('UTILITY_VERIFICATION_REQUIRED')
  result.add(c.kind)
 return result
