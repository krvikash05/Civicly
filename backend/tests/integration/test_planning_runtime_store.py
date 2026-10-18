"""Real FalkorDB/memory draft foundation with no paid providers."""
import asyncio,json,copy
from pathlib import Path
import os
PREFIX=os.environ.get("CIVICLY_PLANNING_EVIDENCE_PREFIX","B12R")
import pytest
from app.active import active_scope
from app.graph.repository import Conflict
from app.services.evidence.models import Actor
from app.services.planning.models import PlanDraft
from app.services.planning.storage import PlanMigration
from app.services.planning.service import PlanningBlocked
from tests.integration.test_memory_graphrag import memory
from tests.b12_fixtures import prepared,ISSUES
pytestmark=pytest.mark.integration
ACTOR=Actor(id='synthetic-b12-planner',role='ANALYST')
@pytest.mark.parametrize('issue',ISSUES)
def test_actual_drafts_all_issues_version_replay_and_ack_loss(db,tmp_path,memory,issue):
 p,r,clock,path,inv,draft,service=prepared(db,tmp_path,memory,issue)
 async def run():
  with active_scope(p):
   with pytest.raises(RuntimeError,match='INJECTED_ACK_LOSS'):await service.create(draft,request_id='B12-first',actor=ACTOR,interrupt='after_commit')
   first=await service.create(draft,request_id='B12-first',actor=ACTOR);replay=await service.create(draft,request_id='B12-first',actor=ACTOR)
   assert first==replay and first.status=='DRAFT' and not first.executable
   assert r._read('MATCH (w:WorkOrder) RETURN count(w)')==[[1]] # authored B10 fixture historical ORDER only
   assert r._read('MATCH (p:ResolutionPlan) RETURN count(p)')==[[1]]
   body=service.store.get(first.id);assert body['draft']==draft.normalized()
   assert r._read('MATCH (:ResolutionPlan {id:$id})-[:HAS_TASK]->(t:ActionTask) RETURN t.status ORDER BY t.id',{'id':first.id})==[['PROPOSED']]*len(draft.tasks)
   if issue=='ROAD_DAMAGE':assert r._read('MATCH (:ResolutionPlan {id:$id})-[:HAS_TASK]->(:ActionTask)-[:DEPENDS_ON]->(:ActionTask) RETURN count(*)',{'id':first.id})==[[1]]
   updated=PlanDraft.model_validate({**draft.model_dump(),'version':2,'previous_plan_id':first.id,'uncertainties':['Prior version retained; no new verified finding']})
   second=await service.create(updated,request_id='B12-next',actor=ACTOR)
   assert second.version==2 and second.plan_hash!=first.plan_hash and service.store.get(first.id)==body
   with pytest.raises(Conflict):await service.create(updated,request_id='B12-first',actor=ACTOR)
   assert PlanMigration(db,p.graph).apply()['ready']
   Path(f'docs/evidence/{PREFIX}-'+issue+'-draft.json').write_text(json.dumps({'mode':'REAL_FALKORDB_SDK_NO_MODEL','source_graph':p.graph,'receipt':first.model_dump(mode='json'),'version2':second.model_dump(mode='json'),'saved':body,'no_new_work_orders':True,'migration':PlanMigration(db,p.graph).status()},indent=2)+'\n')
 asyncio.run(run())

def test_resolver_unknown_conflicting_owner_stale_revoked_and_reference_denials(db,tmp_path,memory):
 p,r,clock,path,inv,draft,service=prepared(db,tmp_path,memory,'WATERLOGGING')
 async def run():
  with active_scope(p):
   # Candidate status is insufficient for accountable ownership.
   edge=r.get_relationship('B12-OWNER-D1');r.update_relationship(edge.id,{'association_status':'CANDIDATE'},expected_hash=edge.content_hash)
   with pytest.raises(PlanningBlocked,match='OWNERSHIP'):await service.create(draft,request_id='owner',actor=ACTOR)
   edge=r.get_relationship(edge.id);r.update_relationship(edge.id,{'association_status':'VERIFIED'},expected_hash=edge.content_hash)
   wrong=draft.model_dump();wrong['tasks'][0]['department_id']='DEPT-WATER'
   with pytest.raises(PlanningBlocked,match='DEPARTMENT_MISMATCH'):await service.create(wrong,request_id='wrong',actor=ACTOR)
   # Raw corruption only this owned isolated graph, never bypass accepted writes.
   r.graph.query('MATCH (a:InfrastructureAsset {id:$asset}),(d:Department {id:$dept}) CREATE (a)-[e:MAINTAINED_BY]->(d) SET e=$props',params={'asset':'D1','dept':'DEPT-WATER','props':{**edge.properties,'id':'B12-CONFLICT','association_status':'VERIFIED'}})
   with pytest.raises(PlanningBlocked,match='OWNERSHIP'):await service.create(draft,request_id='conflict',actor=ACTOR)
   # Remove only this newly inserted corrupt test edge; no graph reset.
   r.graph.query('MATCH ()-[e:MAINTAINED_BY {id:$id}]->() DELETE e',params={'id':'B12-CONFLICT'})
   bad=draft.model_dump();bad['tasks'][0]['target_ids']=['D2']
   with pytest.raises(PlanningBlocked,match='TARGET_OUTSIDE'):await service.create(bad,request_id='foreign',actor=ACTOR)
   future=draft.model_dump();future['tasks'][0]['procedure_citation']['retrieved_at']='2027-01-01T00:00:00Z'
   with pytest.raises(PlanningBlocked,match='CITATION_FROM_FUTURE'):await service.create(future,request_id='future',actor=ACTOR)
   # A source may be authored by coordination while responsibility stays verified Drainage.
   from app.memory.models import sources
   coordination=next(s for s in sources() if s.owner_department_id=='DEPT-COORD')
   await memory.ingest(coordination)
   reference=(await memory.retrieve(as_of=clock(),document_id=coordination.document_id))['citations'][0]
   from app.services.planning.models import TaskDraft
   cross=TaskDraft.model_validate({**draft.tasks[0].model_dump(),'procedure_citation':reference})
   from app.services.evidence.reader import Reader
   resolution=await service.resolve(cross,Reader(r,clock()),clock())
   assert resolution['document_owner_id']=='DEPT-COORD' and resolution['execution_department_id']=='DEPT-DRAIN'
   citation=draft.tasks[0].procedure_citation
   # Supersede the cited version: old citation must not become a current draft.
   from app.memory.models import Source
   source=memory.store.get(citation.canonical_document_id)[0]
   version2=Source.model_validate({**source.model_dump(),'version':2,'supersedes':1,'effective_from':'2026-10-01T00:00:00Z'})
   await memory.ingest(version2)
   with pytest.raises(PlanningBlocked,match='PROCEDURE_STALE'):await service.create(draft,request_id='stale',actor=ACTOR)
   current=draft.model_dump();current['tasks'][0]['procedure_citation']=(await memory.retrieve(as_of=clock(),document_id=source.document_id))['citations'][0]
   memory.store.revoke(version2.id,operator='synthetic-curator',reason='B12 test source withdrawn')
   with pytest.raises(PlanningBlocked,match='PROCEDURE_STALE'):await service.create(current,request_id='revoked',actor=ACTOR)
   assert r._read('MATCH (p:ResolutionPlan) RETURN count(p)')==[[0]]
   Path(f'docs/evidence/{PREFIX}-resolver-denials.json').write_text(json.dumps({'unknown_candidate':True,'conflicting_verified':True,'wrong_department':True,'foreign_target':True,'future_citation':True,'document_owner_not_executor':True,'superseded_source':True,'revoked_source':True,'no_plan_acknowledged':True,'graph':p.graph},indent=2)+'\n')
 asyncio.run(run())
