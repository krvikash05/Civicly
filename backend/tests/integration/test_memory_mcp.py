"""Actual MCP discovery/call, LangGraph and SDK persistence; fake model labeled."""
import asyncio,json,hashlib,os,subprocess
from pathlib import Path
from uuid import uuid4
import pytest
from falkordb import FalkorDB
from graphrag_sdk import ConnectionConfig
from app.active import active_scope
from app.memory.models import sources
from app.memory.runtime import Profile
from app.memory.service import Memory
from app.memory.storage import MemoryMigration
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository
from app.graph.targets import new_test_graph_name
from app.agents.mcp import brokers
from app.agents.runtime import InvestigationAgent
from app.agents.checkpoints import saver
from app.mcp.civicly.contracts import Context
from tests.b10_fixtures import create,state,ScriptedModel,choose
from tests.schema_examples import common
pytestmark=pytest.mark.integration

def test_real_sdk_domain_mcp_agent_checkpoint_and_fresh_process(db,settings,tmp_path):
 proof_prefix=os.environ.get('CIVICLY_MEMORY_TEST_EVIDENCE_PREFIX','B11')
 assert proof_prefix in {'B11','B11R'}
 path=tmp_path/'agent.json';p,r,clock,receipt,inv=create(db,path);docs='civicly_docs_b11_test_'+uuid4().hex
 canonical=new_test_graph_name(11);MigrationRunner(db,canonical).apply();cr=GraphRepository(db,canonical)
 MemoryMigration(db,canonical).apply()
 for id in ['DEPT-DRAIN','DEPT-ROAD','DEPT-WATER','DEPT-SAN','DEPT-COORD']:cr.create_node('Department',{**common(id),'name':id,'department_type':'ENGINEERING'})
 cfg=ConnectionConfig(host=settings.host,port=settings.port,username=settings.username,password=settings.password.get_secret_value() if settings.password else None,graph_name=docs,retry_count=1)
 m=Memory(cr,cfg);user='b11_ro_'+uuid4().hex;password=uuid4().hex+uuid4().hex
 db.connection.execute_command('ACL','SETUSER',user,'reset','on','#'+hashlib.sha256(password.encode()).hexdigest(),'~'+docs,'~'+canonical,'-@all','+ping','+graph.ro_query','+info','+client|setinfo')
 profile=Profile(docs_graph=docs,canonical_graph=canonical,source_graphs=[p.graph],reader_user=user,reader_password=password)
 mp=tmp_path/'memory.json';profile.json_private(mp)
 # Keep this retained exact-key profile private for after-lifecycle fresh retrieval.
 from app.active import save
 retained_agent=Path('.runtime')/('b11-agent-proof-'+uuid4().hex+'.json');save(p,retained_agent)
 retained=Path('.runtime')/('b11-proof-'+uuid4().hex+'.json');profile.json_private(retained)
 async def run():
  # All19 authorized organizational sources, never evaluator artifacts.
  for s in sources():await m.ingest(s)
  with active_scope(p):
   async with brokers(p,path,memory_path=mp,timeout=10) as tools:
    assert len(tools.catalog())==16
    c=Context(trace_id=uuid4().hex,execution_id=uuid4().hex,source_graph=p.graph,investigation_id=inv)
    got=await tools.call('civicly::get_source_document_excerpt',{'document_id':'D001'},c,'Read sourced procedure',cutoff=clock())
    assert got['document_excerpt']['citations'] and got['document_excerpt']['citations'][0]['source_document_id']=='D001'
    c2=Context(trace_id=c.trace_id,execution_id=uuid4().hex,source_graph=p.graph,investigation_id=inv)
    procedures=await tools.call('civicly::get_organizational_procedures',{'department_id':'DEPT-DRAIN','action_type':'INSPECTION'},c2,'Read qualified department procedure',cutoff=clock())
    assert procedures['procedures'] and procedures['procedures'][0]['citation']['owner_department_id']=='DEPT-DRAIN'
    procedure=cr.get_node(procedures['procedures'][0]['procedure_id'],'KnowledgeProcedure')
    assert procedure.properties['status']=='PROPOSED' and procedure.properties['document_ref']==procedures['procedures'][0]['citation']['canonical_document_id']
    water_context=Context(trace_id=c.trace_id,execution_id=uuid4().hex,source_graph=p.graph,investigation_id=inv)
    water=await tools.call('civicly::get_organizational_procedures',{'department_id':'DEPT-WATER','action_type':'INSPECTION'},water_context,'Retrieve eligible procedures despite unrelated chunk crowding',cutoff=clock())
    assert {v['citation']['source_document_id'] for v in water['procedures']}=={'D005','D017'}
    assert any('ELIGIBLE_SOURCE_FALLBACK' in gap for gap in water['data']['gaps'])
    Path('docs/evidence/B11R-mcp-water-proof.json').write_text(json.dumps(water,indent=2)+'\n')
    s=state(p,r,tools,clock,receipt,inv);model=ScriptedModel([choose('READ',{'document_id':'D001'},'civicly::get_source_document_excerpt'),choose()])
    result=await InvestigationAgent(p,r,tools,model,saver(p),clock=clock).run(s,thread_id=s.thread_id)
    assert result['__interrupt__'] and any(o.get('document_excerpt',{}).get('citations') for o in result['data']['observations'])
    resumed=await InvestigationAgent(p,r,tools,ScriptedModel([choose()]),saver(p),clock=clock).run(None,thread_id=s.thread_id,resume=True)
    assert resumed['data']['wakes']==1 and result['data']['executions']==resumed['data']['executions']
    assert model.contexts[-1]['material_observations']
    # Cache keyed only on civic source revision must never hide document revocation.
    prime=Context(trace_id=c.trace_id,execution_id=uuid4().hex,source_graph=p.graph,investigation_id=inv)
    primed=await tools.call('civicly::get_source_document_excerpt',{'document_id':'D001'},prime,'Prime revocation check',cutoff=clock())
    assert primed['document_excerpt']['citations']
    civic_revision=r._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.repo_revision")
    m.store.revoke('ORG:D001:1',operator='synthetic-curator',reason='Explicit test review revocation')
    assert r._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.repo_revision")==civic_revision
    c3=Context(trace_id=c.trace_id,execution_id=uuid4().hex,source_graph=p.graph,investigation_id=inv)
    denied=await tools.call('civicly::get_source_document_excerpt',{'document_id':'D001'},c3,'Verify revoked source denial',cutoff=clock())
    assert tools.last_cache_receipt is None
    assert denied['status']=='UNAVAILABLE' and not denied['document_excerpt']['citations']
    Path('docs/evidence/'+proof_prefix+'-mcp-agent-proof.json').write_text(json.dumps({'mode':'REAL_SDK_MCP_LANGGRAPH_SAVER_SCRIPTED_TEST_MODEL','graph':p.graph,'docs':docs,'canonical_references':canonical,'civic_revision_unchanged_during_revocation':True,'tools':tools.catalog(),'excerpt':got,'procedures':procedures,'thread':s.thread_id,'checkpoint':result['data'],'resumed':resumed['data'],'revoked':denied,'actual_gemini_requests':0},indent=2)+'\n')
 asyncio.run(run())
 # Fresh source D002 remains ready; D001 revoked intentionally. Worker tests D002.
 out=tmp_path/'fresh.json'
 proc=subprocess.run([str(Path('backend/.venv/bin/python').absolute()),'-m','tests.b11_worker',str(mp),str(out),'D002'],env={**os.environ,'PYTHONPATH':'backend'},capture_output=True,timeout=60)
 assert proc.returncode==0,proc.stderr.decode()[-1000:]
 Path('docs/evidence/'+proof_prefix+'-fresh-process-proof.json').write_text(out.read_text())
 reader=FalkorDB(host='127.0.0.1',port=6379,username=user,password=password)
 try:
  with pytest.raises(Exception):reader.select_graph(docs).query('CREATE (:Unauthorized)')
  with pytest.raises(Exception):reader.select_graph('civicly_knowledge').ro_query('RETURN 1')
 finally:reader.connection.close();reader.connection.connection_pool.disconnect()
 Path('docs/evidence/'+proof_prefix+'-persistence-anchor.json').write_text(json.dumps({'private_profile_path':str(retained),'agent_profile_path':str(retained_agent),'source_document_id':'D002','canonical_graph':canonical,'docs_graph':docs,'thread':json.loads(Path('docs/evidence/'+proof_prefix+'-mcp-agent-proof.json').read_text())['thread'],'retrieval':json.loads(out.read_text()),'scope':'retained synthetic B11 proof; credentials excluded'},indent=2)+'\n')
