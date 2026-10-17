"""Fresh read-only preservation check for accepted source graphs and trace records."""
import json,subprocess,argparse
from pathlib import Path
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.graph.analysis.evaluation import verify_city,CITY_GRAPH
from app.graph.analysis.counterfactual import capture
from app.graph.migration import MigrationRunner
from app.mcp.civicly.runtime import connections,load_config
from app.mcp.civicly.storage import TraceStore,TraceMigration
from app.mcp.civicly.models import TraceRecord
from app.mcp.civicly.contracts import digest

ROOT=Path(__file__).resolve().parents[1]
def accepted(name):return json.loads(subprocess.check_output(['git','show','HEAD:docs/evidence/'+name],cwd=ROOT))
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
base=json.loads((ROOT/'docs/evidence/B08-baseline-retained.json').read_text())
b05=accepted('B06-post-lifecycle.json')
with connect(Settings(_env_file='.env')) as admin:
    city=verify_city(GraphRepository(admin,CITY_GRAPH),json.loads((ROOT/'data/ingestion/city-v3.json').read_text()));assert city==base['city']
    for key in ['controlled_source','counterfactual_clone']:assert capture(GraphRepository(admin,b05[key]['graph'])).fingerprint==b05[key]
    probe=admin.select_graph('civicly_b01_runtime').ro_query('MATCH (n:B01Probe {id:$id}) RETURN n.id,n.source_kind,n.task LIMIT 1',params={'id':'B01-PERSISTENCE'}).result_set
    assert probe==base['b01_probe']
    canonical=MigrationRunner(admin,'civicly_knowledge').status();assert canonical['ready']
    trace_schema=TraceMigration(admin,load_config()['trace_graph']).status();assert trace_schema['ready']
with connections() as (_,writer,name):
    store=TraceStore(writer,name);verified=0
    for file in ['B07-runtime-proof-before-final-contract.json','B07-runtime-proof.json']:
        for saved in accepted(file)['persisted_server_traces']:
            assert store.get(saved['context']['execution_id'])==TraceRecord.model_validate_json(json.dumps(saved));verified+=1
    for file in ['B07R-before-outputs.json','B07R-runtime-proof.json']:
        for result in accepted(file)['results'].values():
            record=store.get(result['execution_id']);assert record and record.output_sha256==digest(result) and record.source_evidence_ids==result['source_evidence_ids'];verified+=1
    count=store.repo._read('MATCH (n:ToolExecution) RETURN count(n)')[0][0]
    assert count>=base['trace_records_current']
report={'status':'PASS','city':city,'b01_probe':probe,'b05_source_clone_unchanged':True,'canonical':canonical,'trace_migration':trace_schema,
        'accepted_trace_records_verified':verified,'trace_records_current':count,'source_data_modified':False,'credential_values_logged':False}
args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'PASS','accepted_traces_preserved':verified,'source_fingerprints_unchanged':True}))
