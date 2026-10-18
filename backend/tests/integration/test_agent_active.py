"""Real B08/B09/official+domain MCP integration; no model involved in this boundary test."""
import asyncio,json
from pathlib import Path
import pytest
from falkordb import FalkorDB
from redis.exceptions import NoPermissionError
from app.active import new_profile,save,active_scope,provision,is_shared_target
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository,PreconditionFailed
from app.services.complaints import ComplaintService
from app.services.evidence import EvidenceService
from app.agents.mcp import brokers
from app.mcp.civicly.contracts import Context
from tests.b08_fixtures import populate,payload,CLOCK
from tests.b09_fixtures import ANALYST
from app.services.evidence.policies import POLICIES
from tests.schema_examples import common
from uuid import uuid4

pytestmark=pytest.mark.integration


def test_real_shared_graph_boundary(db,tmp_path):
    p=new_profile();path=tmp_path/'active.json';save(p,path)
    MigrationRunner(db,p.graph).apply();repo=GraphRepository(db,p.graph,lease_seconds=30)
    try:
        populate(repo);repo.create_node('Department',{**common('DEP'),'name':'Synthetic','department_type':'ENGINEERING'})
        with pytest.raises(PreconditionFailed):ComplaintService(repo,clock=lambda:CLOCK).intake(payload())
        with active_scope(p):
            receipt=ComplaintService(repo,clock=lambda:CLOCK).intake(payload())
            inv=EvidenceService(repo,clock=lambda:CLOCK).execute({'operation':'open','request_id':'b10-open','incident_ids':[receipt.incident_id],'cluster_id':receipt.cluster_id},ANALYST).entity_id
            hyp=EvidenceService(repo,clock=lambda:CLOCK).execute({'operation':'propose','request_id':'b10-propose','investigation_id':inv,'incident_ids':[receipt.incident_id],'asset_ids':['D1'],
                'cause_code':'BLOCKAGE','statement':'Blockage requires independent inspection','mechanism':'Restricted flow may explain standing water','confirming_codes':POLICIES['WATERLOGGING']['BLOCKAGE']['confirming'],'falsifying_codes':POLICIES['WATERLOGGING']['BLOCKAGE']['falsifying']},ANALYST).entity_id
            provision(db,p)
            async def check():
                async with brokers(p,path) as tools:
                    calls=[]
                    for id in [receipt.incident_id,receipt.cluster_id,inv,hyp]:
                        ctx=Context(trace_id=uuid4().hex,execution_id=uuid4().hex,source_graph=p.graph,investigation_id=inv)
                        result=await tools.call('official::query_graph_readonly',{'template':'node','id':id},ctx,'Application integration probe; no model selection')
                        assert result['rows'][0]['properties']['id']==id;calls.append(result)
                    ctx=Context(trace_id=uuid4().hex,execution_id=uuid4().hex,source_graph=p.graph,investigation_id=inv)
                    value=await tools.call('civicly::find_related_incidents',{'incident_id':receipt.incident_id,'max_results':10,'as_of':CLOCK},ctx,'Application boundary probe; no model selection')
                    assert value['context']['source_graph']==p.graph and value['graph_revision']==calls[-1]['graph_revision']
                    assert any(n['id']==receipt.incident_id for n in value['data']['nodes'])
                    return {'official':calls,'domain':value,'catalog':tools.catalog(),'transport':tools.traces}
            result=asyncio.run(check())
        assert not is_shared_target(p.graph)
        read=FalkorDB(host='127.0.0.1',port=6379,username=p.read_user,password=p.read_password.get_secret_value(),socket_timeout=3)
        try:
            for cmd in [('GRAPH.QUERY',p.graph,'CREATE (:Forbidden)'),('GRAPH.RO_QUERY','civicly_knowledge','RETURN 1')]:
                with pytest.raises(NoPermissionError):read.connection.execute_command(*cmd)
        finally:read.connection.close();read.connection.connection_pool.disconnect()
        checkpoint=FalkorDB(host='127.0.0.1',port=6379,username=p.checkpoint_user,password=p.checkpoint_password.get_secret_value(),socket_timeout=3)
        try:
            assert checkpoint.select_graph(p.checkpoints).query('RETURN 1').result_set==[[1]]
            for command in ['GRAPH.QUERY','GRAPH.RO_QUERY']:
                with pytest.raises(NoPermissionError):checkpoint.connection.execute_command(command,p.graph,'RETURN 1')
        finally:checkpoint.connection.close();checkpoint.connection.connection_pool.disconnect()
        result.update(checkpoint_cross_source_denials=True,graph=p.graph,incident=receipt.incident_id,investigation=inv,hypothesis=hyp,read_only_denials=True)
        Path('/tmp/civicly-b10-active-proof.json').write_text(json.dumps(result,indent=2))
    finally:
        for owned in [p.graph,p.checkpoints]:
            if owned in db.list_graphs():db.select_graph(owned).delete()
        for user in [p.read_user,p.checkpoint_user]:db.connection.execute_command('ACL','DELUSER',user)
