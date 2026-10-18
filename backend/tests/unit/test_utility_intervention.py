"""Closed utility policy tests; fake reader only, no runtime claims."""
from types import SimpleNamespace as NS
from copy import deepcopy
import pytest
from pydantic import ValidationError
from app.services.planning.models import PlanDraft
from app.services.planning.utility import validate_dependencies
from app.services.planning.policy import validate_remediation
from app.services.planning.service import PlanningBlocked
from app.services.operations.service import execution_gates
from app.services.operations import utility
from app.services.evidence.models import Observation
from app.graph.repository import PreconditionFailed
from tests.b12_fixtures import sample
T0='2026-10-19T12:00:00.000000Z';T1='2026-10-19T12:01:00.000000Z';T2='2026-10-19T12:02:00.000000Z'
def draft():
 value=sample();value['issue']='ROAD_DAMAGE';value['monitoring'].update(issue='ROAD_DAMAGE',required_evidence=['WEAR_EXPOSURE','FOLLOWUP_PAVEMENT'])
 t=value['tasks'][0];t.update(id='isolate',action_type='UTILITY_ISOLATION',target_ids=['P'],department_id='DEPT-WATER',remediation={'mode':'SUPPORTED_NOW','conditions':[{'kind':k,'status':'MET','evidence_ids':['EV']} for k in ['CAUSAL_INSPECTION','SAFETY_REVIEW']]})
 repair=deepcopy(t);repair.update(id='repair',action_type='UTILITY_LEAK_REPAIR',depends_on=['isolate']);repair['remediation']['mode']='CONDITIONAL';repair['remediation']['conditions'].append({'kind':'ISOLATION_PROOF','status':'UNMET','depends_on_task_id':'isolate'})
 value['tasks'].append(repair);return PlanDraft.model_validate(value)
def reject(code):raise PreconditionFailed(code)
@pytest.mark.parametrize('change,code',[(None,None),('missing','UTILITY_DEPENDENCY_REQUIRED'),('met','UTILITY_DEPENDENCY_BINDING'),('wrong_action','UTILITY_DEPENDENCY_BINDING'),('wrong_target','UTILITY_DEPENDENCY_TARGET'),('unmet_safety','UTILITY_CURRENT_EVIDENCE_REQUIRED'),('extra_dependency','UTILITY_DEPENDENCY_SCOPE')])
def test_closed_dependency(change,code):
 d=draft();t=d.tasks[1]
 if change=='missing':t.remediation.conditions.pop()
 if change=='met':t.remediation.conditions[-1]=t.remediation.conditions[-1].model_copy(update={'status':'MET'})
 if change=='wrong_action':d.tasks[0]=d.tasks[0].model_copy(update={'action_type':'INSPECTION'})
 if change=='wrong_target':d.tasks[0]=d.tasks[0].model_copy(update={'target_ids':['OTHER']})
 if change=='unmet_safety':t.remediation.conditions[1]=t.remediation.conditions[1].model_copy(update={'status':'UNMET'})
 if change=='extra_dependency':t.depends_on.append('another')
 if code:
  with pytest.raises(PreconditionFailed,match=code):validate_dependencies(t,d,NS(),reject)
 else:validate_dependencies(t,d,NS(),reject)
@pytest.mark.parametrize('fulfilled,status,ok',[(set(),'COMPLETED',False),({'ISOLATION_PROOF'},'IN_PROGRESS',False),({'ISOLATION_PROOF'},'COMPLETED',True)])
def test_execution_proof(fulfilled,status,ok):
 if ok:execution_gates(draft().tasks[1],[status],fulfilled)
 else:
  with pytest.raises(PreconditionFailed):execution_gates(draft().tasks[1],[status],fulfilled)
@pytest.mark.parametrize('assessment,reviewed,contradiction',[('CONTRADICTED',[],['EV']),('SUPPORTED',['EV'],['EV']),('POSSIBLE',[],[]),('INCONCLUSIVE',[],[])])
def test_negative_causal_evidence(assessment,reviewed,contradiction):
 d=draft();a=NS(id='A1',cause_code='UTILITY_LEAK',assessment=assessment,classification=NS(reviewed_support_ids=reviewed,reviewed_contradiction_ids=contradiction,unreviewed_contradiction_ids=[]))
 with pytest.raises(PlanningBlocked,match='REMEDIAL_EVIDENCE_INSUFFICIENT'):validate_remediation(d.tasks[0],d,NS(),[a],PlanningBlocked)
def ob(code,at=T1,result='OBSERVED',asset='P'):
 return Observation.model_validate({'asset_id':asset,'code':code,'statement':'Explicit synthetic check','method':'DIRECT_SYNTHETIC_FIELD_TEST','observed_at':at,'result':result})
@pytest.mark.parametrize('codes,status',[(list(utility.FOLLOWUP),'INCONCLUSIVE'),(['POST_REPAIR_PRESSURE_NORMAL','POST_REPAIR_LEAK_ABSENT'],'UTILITY_VERIFIED'),(['POST_REPAIR_PRESSURE_ABNORMAL','POST_REPAIR_LEAK_ABSENT'],'PROBLEM_PERSISTS'),(['POST_REPAIR_PRESSURE_NORMAL','POST_REPAIR_LEAK_PRESENT'],'PROBLEM_PERSISTS'),(['POST_REPAIR_PRESSURE_NORMAL'],'MONITORING'),([],'MONITORING')])
def test_postrepair_component(codes,status):
 actual,_=utility.evaluate(['P'],[ob(c) for c in codes],T1,T2,T0,T2);assert actual==status
@pytest.mark.parametrize('kind',['unknown','other_target','early','unreviewed','missing'])
def test_missing_isolation_proof(kind):
 observations=[] if kind=='missing' else [ob(utility.ISOLATION,at=T0 if kind=='early' else T1,result='UNKNOWN' if kind=='unknown' else 'OBSERVED',asset='OTHER' if kind=='other_target' else 'P')]
 refs=[NS(report=NS(review=None if kind=='unreviewed' else True,source_kind='SYNTHETIC',observations=observations))]
 with pytest.raises(PreconditionFailed,match='REVIEWED_ISOLATION_REQUIRED'):utility.isolation_proof(refs,['P'],T1)
@pytest.mark.parametrize('linked,guard,ok',[(True,False,False),(True,True,True),(False,True,False),(False,False,True)])
def test_road_dependency(linked,guard,ok):
 d=draft();t=d.tasks[0].model_copy(deep=True,update={'id':'road','action_type':'SUBGRADE_REPAIR','target_ids':['R'],'depends_on':[]})
 if guard:t.depends_on.append('repair');t.remediation.conditions.append(NS(kind='UTILITY_VERIFICATION',status='UNMET',evidence_ids=[],depends_on_task_id='repair'))
 d.tasks.append(t);reader=NS(topology=lambda *a,**kw:NS(truncated=False,edges=[NS(id='EDGE',kind='UNDERLIES')],paths=[NS(node_ids=('P','R'),edge_ids=('EDGE',),directions=('OUTGOING',))] if linked else []))
 if ok:validate_dependencies(t,d,reader,reject)
 else:
  with pytest.raises(PreconditionFailed):validate_dependencies(t,d,reader,reject)
def test_legacy_hash_and_unknown_action():
 value=sample();old=PlanDraft.model_validate(value).content_hash
 assert old=='b2c0f93a682d2eae59ced8c4102fe087d146bfacb40c9f601148ea70d8126d29' # Accepted B12 inspection-only normalization.
 value['tasks'][0]['action_type']='ARBITRARY_REPAIR'
 with pytest.raises(ValidationError):PlanDraft.model_validate(value)

@pytest.mark.parametrize('kind',['duplicate','unknown','met_dynamic','no_dynamic_reference'])
def test_closed_prerequisite_input(kind):
 value=draft().model_dump(mode='json');conditions=value['tasks'][1]['remediation']['conditions']
 if kind=='duplicate':conditions.append(dict(conditions[0]))
 if kind=='unknown':conditions[-1]['kind']='UNRESTRICTED_CLEARANCE'
 if kind=='met_dynamic':conditions[-1].update(status='MET',evidence_ids=['EV'])
 if kind=='no_dynamic_reference':conditions[-1]['depends_on_task_id']=None
 if kind in {'duplicate','unknown','met_dynamic'}:
  with pytest.raises(ValidationError):PlanDraft.model_validate(value)
 else:
  d=PlanDraft.model_validate(value)
  with pytest.raises(PreconditionFailed):validate_dependencies(d.tasks[1],d,NS(),reject)
@pytest.mark.parametrize('damage',['unknown','old','other_target','numeric'])
def test_utility_outcome_not_inferred(damage):
 rows=[ob('POST_REPAIR_PRESSURE_NORMAL'),ob('POST_REPAIR_LEAK_ABSENT')]
 if damage=='unknown':rows[0]=ob('POST_REPAIR_PRESSURE_NORMAL',result='UNKNOWN')
 if damage=='old':rows[0]=ob('POST_REPAIR_PRESSURE_NORMAL',at=T0)
 if damage=='other_target':rows[0]=ob('POST_REPAIR_PRESSURE_NORMAL',asset='OTHER')
 if damage=='numeric':rows[0]=rows[0].model_copy(update={'value':1.0,'unit':'bar'})
 if damage in {'old','numeric'}:
  with pytest.raises(PreconditionFailed):utility.evaluate(['P'],rows,T1,T2,T0,T2)
 else:assert utility.evaluate(['P'],rows,T1,T2,T0,T2)[0]=='MONITORING'

@pytest.mark.parametrize('case,expected',[
 ('two_same_road','UTILITY_MULTIPLE_REPAIR_PREDECESSORS'),
 ('two_road_targets','UTILITY_MULTIPLE_REPAIR_PREDECESSORS'),
 ('fresh_second_link','UTILITY_MULTIPLE_REPAIR_PREDECESSORS'),
 ('sole_substituted','UTILITY_DEPENDENCY_BINDING'),
 ('sole_omitted','UTILITY_DEPENDENCY_REQUIRED'),
 ('dependency_substituted','UTILITY_DEPENDENCY_BINDING'),
 ('valid_single',None),('unlinked_other_repair',None),
 ('missing_target','UTILITY_DEPENDENCY_TARGET'),
 ('extra_dependency','UTILITY_DEPENDENCY_SCOPE'),
 ('no_linked_repair',None),
])
def test_complete_road_binding(case,expected):
 value=draft().model_dump(mode='json');isolate=deepcopy(value['tasks'][0]);isolate.update(id='isolate2',target_ids=['P2'])
 repair=deepcopy(value['tasks'][1]);repair.update(id='repair2',target_ids=['P2'],depends_on=['isolate2']);repair['remediation']['conditions'][-1]['depends_on_task_id']='isolate2'
 road=deepcopy(value['tasks'][0]);road.update(id='road',action_type='SUBGRADE_REPAIR',department_id='DEPT-ROAD',target_ids=['R'],depends_on=['repair']);road['remediation'].update(mode='CONDITIONAL');road['remediation']['conditions'].append({'kind':'UTILITY_VERIFICATION','status':'UNMET','depends_on_task_id':'repair'})
 value['tasks'] += [isolate,repair,road];links={'P':{'R'},'P2':set()}
 if case=='two_same_road':links['P2']={'R'}
 if case=='two_road_targets':road['target_ids']=['R','R2'];links['P2']={'R2'}
 if case=='sole_substituted':road['depends_on']=['repair2'];road['remediation']['conditions'][-1]['depends_on_task_id']='repair2'
 if case in {'sole_omitted','no_linked_repair'}:road['depends_on']=[];road['remediation']['conditions'].pop();road['remediation']['mode']='SUPPORTED_NOW'
 if case=='no_linked_repair':links['P']=set()
 if case=='dependency_substituted':road['depends_on']=['repair2']
 if case=='missing_target':road['target_ids']=['R','R2']
 if case=='extra_dependency':road['depends_on'].append('repair2')
 d=PlanDraft.model_validate(value) # All ten drafts are schema-valid.
 def topology(q):
  targets=sorted(links[q.source_id]);return NS(truncated=False,edges=[NS(id=t,kind='UNDERLIES') for t in targets],paths=[NS(node_ids=(q.source_id,t),edge_ids=(t,),directions=('OUTGOING',)) for t in targets])
 reader=NS(topology=topology)
 if case=='fresh_second_link':
  validate_dependencies(d.tasks[-1],d,reader,reject)
  links['P2']={'R'} # Same immutable draft, fresh topology before new authority.
 if expected:
  with pytest.raises(PreconditionFailed,match='^'+expected+'$'):validate_dependencies(d.tasks[-1],d,reader,reject)
 else:validate_dependencies(d.tasks[-1],d,reader,reject)

@pytest.mark.parametrize('duplicate',['condition','depends_on','task_id'])
def test_road_duplicate_references_remain_schema_rejected(duplicate):
 value=draft().model_dump(mode='json');t=value['tasks'][1]
 if duplicate=='condition':t['remediation']['conditions'].append(deepcopy(t['remediation']['conditions'][-1]))
 if duplicate=='depends_on':t['depends_on'].append(t['depends_on'][0])
 if duplicate=='task_id':value['tasks'].append(deepcopy(t))
 with pytest.raises(ValidationError):PlanDraft.model_validate(value)
