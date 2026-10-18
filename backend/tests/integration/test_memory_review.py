"""B11-R actual SDK/FalkorDB regression; all corruption isolated, no live LLM."""
import asyncio,json
from pathlib import Path
from uuid import uuid4
import pytest
from app.memory.models import sources,SourceError
from app.memory.sdk import SDK
from app.active import active_scope
from app.mcp.civicly.service import CivicReadService
from app.mcp.civicly.contracts import Context
from tests.integration.test_memory_graphrag import memory,AT
from tests.b10or2_fixtures import prepare
from tests.b09_fixtures import Fixture,assess,propose
pytestmark=pytest.mark.integration

def proof(name,value):
 Path('docs/evidence/B11R-'+name+'.json').write_text(json.dumps(value,indent=2)+'\n')

def test_all_seeded_department_action_pairs_survive_global_crowding(memory):
 async def run():
  corpus=sources()
  for s in corpus:await memory.ingest(s)
  sdk=SDK(memory.config,readonly=True)
  try:global_ids={i.metadata['chunk_id'] for i in (await sdk.retrieve('INSPECTION')).items}
  finally:await sdk.close()
  water=[s for s in corpus if s.owner_department_id=='DEPT-WATER']
  assert {s.document_id for s in water}=={'D005','D017'}
  assert all(c['id'] not in global_ids for s in water for c in memory.store.get(s.id)[1]),'Real corpus must reproduce global top-k crowding'
  rows=[]
  for department,action in sorted({(s.owner_department_id,a) for s in corpus for a in s.action_types}):
   eligible=[s for s in corpus if s.owner_department_id==department and action in s.action_types]
   got=await memory.retrieve(as_of=AT,department_id=department,action_type=action)
   assert got['citations'],(department,action,got)
   assert {c['source_document_id'] for c in got['citations']}=={s.document_id for s in eligible}
   for c in got['citations']:
    source=next(s for s in eligible if s.document_id==c['source_document_id'])
    assert c['source_version']==source.version and c['owner_department_id']==department and c['content_checksum']==source.sha256
    chunks=memory.store.get(source.id)[1]
    assert any(c['quote_excerpt']==v['text'][:800] and c['chunk_sha256']==v['sha256'] for v in chunks)
   rows.append({'department':department,'action':action,'result':got})
  proof('corpus',{'sdk_graph':memory.config.graph_name,'global_inspection_top12':sorted(global_ids),'pairs':rows})
 asyncio.run(run())

@pytest.mark.parametrize('damage',['missing','wrong_vector','missing_index'])
def test_replay_checks_required_indexing_state(memory,damage):
 async def run():
  s=sources()[0];first=await memory.ingest(s);healthy=await memory.ingest(s)
  assert healthy['replayed'] and healthy['chunks']==first['chunks']
  graph=memory.repo.client.select_graph(memory.config.graph_name)
  if damage=='missing':graph.query('MATCH (:Document {id:$id})-[:PART_OF]->(c:Chunk) REMOVE c.embedding',params={'id':s.id})
  elif damage=='wrong_vector':graph.query('MATCH (:Document {id:$id})-[:PART_OF]->(c:Chunk) SET c.embedding=vecf32($v)',params={'id':s.id,'v':[1.0]*64})
  else:graph.query('DROP VECTOR INDEX FOR (c:Chunk) ON (c.embedding)')
  with pytest.raises(SourceError,match='SDK_PARTIAL_REQUIRES_REPAIR'):await memory.ingest(s)
  with pytest.raises(SourceError,match='SDK_PARTIAL_REQUIRES_REPAIR'):await memory.retrieve(as_of=AT,document_id=s.document_id)
  proof('index-'+damage,{'graph':memory.config.graph_name,'healthy_replay':healthy['replayed'],'damage':damage,'broken_replay':'REPAIR_REQUIRED','broken_retrieval':'REPAIR_REQUIRED'})
 asyncio.run(run())

def test_latest_assessment_budget_and_history_beyond_hard_cap(db,tmp_path):
 p,r,clock,receipt,inv,h=prepare(db,tmp_path/'agent.json','WATERLOGGING')
 with active_scope(p):
  service=CivicReadService(db,source_graph=p.graph)
  def read(limit,at=None):
   return service.run('retrieve_case_memory',{'investigation_id':inv,'max_results':limit,'as_of':at or clock()},Context(trace_id=uuid4().hex,execution_id=uuid4().hex,source_graph=p.graph,investigation_id=inv))
  latest=r._read('MATCH (:Hypothesis {id:$id})-[:HAS_ASSESSMENT]->(a:HypothesisAssessment) RETURN a.id ORDER BY a.assessed_at DESC,a.id DESC LIMIT 1',{'id':h})[0][0]
  small=read(1);assert json.loads(small['cases'][0]['outcome_summary'])['assessment_id']==latest
  assert small['truncated'] and any('OMITTED_PREDECESSOR' in x for x in small['data']['gaps'])
  f=Fixture(r,clock,{'WATERLOGGING':receipt},p.graph,{})
  cutoff=clock();ids=[]
  clock.advance()
  second_hypothesis=propose(f,inv,ref='B11R-second-hypothesis')
  # More than101 per investigation, within unchanged B09 <=100 per hypothesis.
  for n in range(96):ids.append(assess(f,second_hypothesis,ref='B11R-correction-'+str(n)).entity_id)
  long=read(100)
  rows=[json.loads(v['outcome_summary']) for v in long['cases']]
  assert len(rows)==100 and rows[-1]['assessment_id']==ids[-1] and long['truncated']
  assert [(v['assessed_at'],v['assessment_id']) for v in rows]==sorted((v['assessed_at'],v['assessment_id']) for v in rows)
  returned={v['assessment_id'] for v in rows};assert rows[0]['previous_assessment_id'] not in returned
  assert all(v['previous_assessment_id'] not in long['source_evidence_ids'] for v in rows)
  newest=read(1);assert json.loads(newest['cases'][0]['outcome_summary'])['assessment_id']==ids[-1]
  historical=read(1,cutoff);assert json.loads(historical['cases'][0]['outcome_summary'])['assessment_id']==latest
  proof('history',{'graph':p.graph,'small':small,'long':long,'historical':historical,'authored_assessments':104})
