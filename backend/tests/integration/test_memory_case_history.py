"""Actual B09 corrected assessment history through existing MCP memory tool."""
import asyncio,json
from pathlib import Path
from uuid import uuid4
import pytest
from app.active import active_scope
from app.agents.mcp import brokers
from app.mcp.civicly.contracts import Context
from tests.b10or2_fixtures import prepare
pytestmark=pytest.mark.integration

def test_actual_episodic_semantic_history_preserves_assessment_revisions(db,tmp_path):
 path=tmp_path/'profile.json';p,r,clock,receipt,inv,h=prepare(db,path,'WATERLOGGING')
 async def run():
  with active_scope(p):
   async with brokers(p,path) as tools:
    c=Context(trace_id=uuid4().hex,execution_id=uuid4().hex,source_graph=p.graph,investigation_id=inv)
    result=await tools.call('civicly::retrieve_case_memory',{'investigation_id':inv,'max_results':100},c,'Retrieve persisted assessment corrections',cutoff=clock())
    assert len(result['cases'])==8
    rows=[json.loads(v['outcome_summary']) for v in result['cases']]
    assert len({v['assessment_id'] for v in rows})==8 and all(v['rule_version'] for v in rows)
    assert [v['assessed_at'] for v in rows]==sorted(v['assessed_at'] for v in rows)
    assert any(v['previous_assessment_id'] for v in rows) and result['source_evidence_ids']
    assert all('not new proof' in v['relevance_reason'] for v in result['cases'])
    Path('docs/evidence/B11-case-memory-proof.json').write_text(json.dumps(result,indent=2)+'\n')
 asyncio.run(run())
