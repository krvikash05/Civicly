"""Fresh administrative read-only retained-domain and durable-trace verification."""
import argparse,json
from pathlib import Path
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.graph.analysis.evaluation import verify_city,CITY_GRAPH
from app.graph.analysis.counterfactual import capture
from app.graph.migration import MigrationRunner
from app.mcp.civicly.runtime import load_config,connections
from app.mcp.civicly.storage import TraceStore,TraceMigration
from app.mcp.civicly.models import TraceRecord
p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args()
old=json.loads(Path('docs/evidence/B06-post-lifecycle.json').read_text())
with connect(Settings(_env_file='.env')) as admin:
 city=verify_city(GraphRepository(admin,CITY_GRAPH),json.loads(Path('data/ingestion/city-v3.json').read_text()));assert city==old['city']
 for key in ['controlled_source','counterfactual_clone']:
  assert capture(GraphRepository(admin,old[key]['graph'])).fingerprint==old[key]
 probe=admin.select_graph('civicly_b01_runtime').ro_query('MATCH (n:B01Probe {id:$id}) RETURN n.id,n.source_kind,n.task LIMIT 1',params={'id':'B01-PERSISTENCE'}).result_set
 assert probe==old['original_b01_probe']
 canonical=MigrationRunner(admin,'civicly_knowledge').status();assert canonical['ready']
 cfg=load_config();trace_schema=TraceMigration(admin,cfg['trace_graph']).status();assert trace_schema['ready']
proof=json.loads(Path('docs/evidence/B07-runtime-proof-before-final-contract.json').read_text())
with connections() as (_,writer,name):
 store=TraceStore(writer,name)
 for saved in proof['persisted_server_traces']:
  assert store.get(saved['context']['execution_id'])==TraceRecord.model_validate_json(json.dumps(saved))
 count=store.repo._read('MATCH (n:ToolExecution) RETURN count(n)')[0][0]
result={'status':'PASS','city':city,'b01_probe':probe,'retained_b05_source_and_clone_unchanged':True,'canonical':canonical,
        'trace_migration':trace_schema,'preexisting_trace_records_preserved':len(proof['persisted_server_traces']),
        'trace_records_current':count,'trace_graph':name,'credential_values_logged':False}
a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','old_traces_preserved':len(proof['persisted_server_traces']),'source_unchanged':True}))
