"""Real FalkorDB + B11 SDK/source pipeline; no model/provider or field execution."""
import asyncio,copy,json
from pathlib import Path
import pytest
from app.active import active_scope
from app.services.evidence.models import Actor
from app.services.planning.service import PlanningBlocked
from app.services.planning.models import PlanDraft
from tests.b12_fixtures import prepared,ISSUES
from tests.integration.test_memory_graphrag import memory
pytestmark=pytest.mark.integration
ACTOR=Actor(id='synthetic-b12r-planner',role='ANALYST')
@pytest.mark.parametrize('issue',ISSUES)
def test_supported_remediation_conditional_and_guards(db,tmp_path,memory,issue):
 p,r,clock,path,inv,draft,service=prepared(db,tmp_path,memory,issue,remedial=True)
 async def run():
  with active_scope(p):
   before={kind:r._read(f'MATCH (n:{kind}) RETURN count(n)')[0][0] for kind in ['WorkOrder','Inspection','InspectionReport','InterventionOutcome']}
   receipt=await service.create(draft,request_id='B12R-remedy',actor=ACTOR)
   saved=service.store.get(receipt.id);assert saved['draft']==draft.normalized() and not receipt.executable
   task=draft.tasks[0];proof=saved['proof']['tasks'][task.id]
   assert proof['remediation']['mode']=='SUPPORTED_NOW' and proof['procedure_status']=='PROPOSED' and not proof['remediation']['unmet_guards']
   assert saved['draft']['tasks'][0]['procedure_citation']['source_document_id'] in {'D019','D020','D021'}
   assert await service.create(draft,request_id='B12R-remedy',actor=ACTOR)==receipt
   # Native previous-version/hash safety used, not a new write path.
   base={**draft.model_dump(mode='json'),'version':2,'previous_plan_id':receipt.id}
   bad=copy.deepcopy(base);bad['tasks'][0]['remediation']['conditions'][0]['evidence_ids']=[]
   from pydantic import ValidationError
   with pytest.raises(ValidationError):await service.create(bad,request_id='B12R-text-bypass',actor=ACTOR)
   bad=copy.deepcopy(base);bad['tasks'][0]['remediation']['conditions'][0].update(status='UNMET',evidence_ids=[],depends_on_task_id='missing-inspection');bad['tasks'][0]['remediation']['mode']='CONDITIONAL'
   with pytest.raises(PlanningBlocked,match='PREREQUISITE_INSPECTION_DEPENDENCY'):await service.create(bad,request_id='B12R-missing-inspection',actor=ACTOR)
   bad=copy.deepcopy(base);bad['issue']=next(i for i in ISSUES if i!=issue);bad['monitoring']['issue']=bad['issue']
   # More precise unsupported remediation: incompatible target policy while valid issue/investigation.
   bad=copy.deepcopy(base);bad['tasks'][0]['action_type']=next(a for a in ['DRAIN_BLOCKAGE_CLEARANCE','SUBGRADE_REPAIR','MISSED_PICKUP_RECOVERY'] if a!=task.action_type)
   with pytest.raises(PlanningBlocked,match='ACTION_TARGET_OR_DEPARTMENT'):await service.create(bad,request_id='B12R-unsupported',actor=ACTOR)
   conditional=copy.deepcopy(base);t=conditional['tasks'][0];t['remediation']['mode']='CONDITIONAL'
   t['remediation']['conditions'][0].update(status='UNMET',evidence_ids=[],depends_on_task_id='inspection-first');t['depends_on']=['inspection-first']
   inspection=copy.deepcopy(t);inspection.update(id='inspection-first',action_type='INSPECTION',remediation=None,depends_on=[])
   from app.memory.models import sources
   source=next(s for s in sources() if s.owner_department_id==t['department_id'] and s.document_id!='D001-PDF')
   inspection['procedure_citation']=(await memory.retrieve(as_of=clock(),document_id=source.document_id))['citations'][0]
   conditional['tasks'].append(inspection)
   second=await service.create(conditional,request_id='B12R-conditional',actor=ACTOR)
   assert service.store.get(second.id)['proof']['tasks'][task.id]['remediation']['unmet_guards']==['CAUSAL_INSPECTION']
   assert service.store.get(receipt.id)==saved
   after={kind:r._read(f'MATCH (n:{kind}) RETURN count(n)')[0][0] for kind in before};assert before==after
   Path('docs/evidence/B12R-'+issue+'-remedial.json').write_text(json.dumps({'mode':'REAL_FALKORDB_B11_SDK_NO_PROVIDER','graph':p.graph,'supported':saved,'conditional':service.store.get(second.id),'operational_counts_before':before,'operational_counts_after':after},indent=2)+'\n')
 asyncio.run(run())
def test_insufficient_causal_support_requires_inspection(db,tmp_path,memory):
 p,r,clock,path,inv,draft,service=prepared(db,tmp_path,memory,'WATERLOGGING')
 async def run():
  with active_scope(p):
   v=draft.model_dump(mode='json');t=v['tasks'][0];t.update(action_type='DRAIN_BLOCKAGE_CLEARANCE',remediation={'mode':'CONDITIONAL','conditions':[{'kind':k,'status':'UNMET','depends_on_task_id':None,'evidence_ids':[]} for k in ['CAUSAL_INSPECTION','SAFETY_REVIEW']]})
   with pytest.raises(PlanningBlocked,match='REMEDIAL_EVIDENCE_INSUFFICIENT'):await service.create(v,request_id='B12R-insufficient',actor=ACTOR)
   assert r._read('MATCH (n:ResolutionPlan) RETURN count(n)')==[[0]]
   receipt=await service.create(draft,request_id='B12R-inspection-available',actor=ACTOR);assert service.store.get(receipt.id)['draft']['tasks'][0]['action_type']=='INSPECTION'
 asyncio.run(run())
