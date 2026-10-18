"""Closed demo proposal policies; never approval or physical verification."""
from app.services.evidence.policies import POLICIES
ACTIONS={
 'DRAIN_BLOCKAGE_CLEARANCE':{'issue':'WATERLOGGING','cause':'BLOCKAGE','labels':['DrainInlet','DrainSegment'],'department':'DEPT-DRAIN','safety_code':'DRAIN_CLEARANCE_SAFETY_REVIEWED'},
 'SUBGRADE_REPAIR':{'issue':'ROAD_DAMAGE','cause':'SUBGRADE_FAILURE','labels':['RoadSegment'],'department':'DEPT-ROAD','safety_code':'SUBGRADE_REPAIR_SAFETY_REVIEWED'},
 'MISSED_PICKUP_RECOVERY':{'issue':'WASTE_ACCUMULATION','cause':'MISSED_PICKUP','labels':['WasteCollectionPoint'],'department':'DEPT-SAN','safety_code':'PICKUP_RECOVERY_SAFETY_REVIEWED'},
 'UTILITY_ISOLATION':{'issue':'ROAD_DAMAGE','cause':'UTILITY_LEAK','labels':['WaterPipe'],'department':'DEPT-WATER','safety_code':'UTILITY_SAFETY_REVIEWED'},
 'UTILITY_LEAK_REPAIR':{'issue':'ROAD_DAMAGE','cause':'UTILITY_LEAK','labels':['WaterPipe'],'department':'DEPT-WATER','safety_code':'UTILITY_SAFETY_REVIEWED'},
}

def validate_remediation(task,draft,reader,assessments,blocked):
 if task.action_type=='INSPECTION':return None
 policy=ACTIONS[task.action_type]
 def reject(code):raise blocked(code,task_id=task.id)
 if draft.issue!=policy['issue'] or task.department_id!=policy['department']:reject('ACTION_TARGET_OR_DEPARTMENT')
 addressed={b.assessment_id for b in draft.basis if b.addressed}
 selected=[a for a in assessments if a.id in set(task.assessment_ids)&addressed and a.cause_code==policy['cause']]
 if not selected or any(a.assessment not in {'SUPPORTED','VERIFIED'} or not a.classification or not a.classification.reviewed_support_ids or a.classification.reviewed_contradiction_ids or a.classification.unreviewed_contradiction_ids for a in selected):reject('REMEDIAL_EVIDENCE_INSUFFICIENT')
 conditions={c.kind:c for c in task.remediation.conditions};tasks={t.id:t for t in draft.tasks}
 from .utility import validate_dependencies
 validate_dependencies(task,draft,reader,reject)
 if task.remediation.mode=='SUPPORTED_NOW' and task.depends_on:reject('PREREQUISITE_FUTURE_DEPENDENCY')
 supporting={id for a in selected for id in a.classification.reviewed_support_ids}&set(task.evidence_ids)
 references={id:reader.evidence(id) for id in supporting}
 for a in selected:
  prior={ref.id:ref for ref in a.evidence_references}
  for id in set(a.classification.reviewed_support_ids)&supporting:
   if id not in prior or prior[id].content_hash!=references[id].content_hash or prior[id].finding_hashes!=references[id].finding_hashes:reject('REMEDIAL_EVIDENCE_CHANGED')
 reports={id:ref.report for id,ref in references.items()}
 # Reader verifies original B09 journal, report, findings, source, dates and review.
 def codes(ids,target):
  return {ob.code for id in ids if id in reports and reports[id] and reports[id].review for ob in reports[id].observations if ob.asset_id==target and ob.result=='OBSERVED'}
 confirming=set(POLICIES[draft.issue][policy['cause']]['confirming'])
 for target in task.target_ids:
  asset=reader.node(target,'InfrastructureAsset')
  if not set(asset.labels)&set(policy['labels']):reject('ACTION_TARGET_OR_DEPARTMENT')
  related=[a for a in selected if target in {e.target for e in reader.edges('CONCERNS',source=a.hypothesis_id)}]
  related_ids={id for a in related for id in a.classification.reviewed_support_ids}&supporting
  if not related or not codes(related_ids,target)&confirming:reject('REMEDIAL_EVIDENCE_INSUFFICIENT')
  for kind,condition in conditions.items():
   if kind in {'ISOLATION_PROOF','UTILITY_VERIFICATION'}:continue
   if condition.status=='MET':
    required=confirming if kind=='CAUSAL_INSPECTION' else {policy['safety_code']}
    if not set(condition.evidence_ids)<=related_ids or not required<=codes(condition.evidence_ids,target):reject('PREREQUISITE_EVIDENCE_INVALID')
   elif kind=='CAUSAL_INSPECTION':
    dependency=tasks.get(condition.depends_on_task_id)
    if not dependency or dependency.id not in task.depends_on or dependency.action_type!='INSPECTION' or target not in dependency.target_ids:reject('PREREQUISITE_INSPECTION_DEPENDENCY')
   elif condition.depends_on_task_id is not None:reject('PREREQUISITE_SAFETY_BINDING')
 return {'mode':task.remediation.mode,'cause_code':policy['cause'],'assessment_ids':[a.id for a in selected],'assessment_statuses':[a.assessment for a in selected],'causal_status':'QUALIFIED_PROPOSAL_ONLY','unmet_guards':[c.kind for c in task.remediation.conditions if c.status=='UNMET'],'execution_authority':False}
