"""Administrative read-only retained-evidence check; no oracle or graph mutation."""
import argparse
import json
from pathlib import Path
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.graph.migration import MigrationRunner
from app.graph.analysis.evaluation import verify_city,CITY_GRAPH
from app.graph.analysis.counterfactual import capture
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
root=Path.cwd();old=json.loads((root/'docs/evidence/B05-post-lifecycle.json').read_text())
with connect(Settings(_env_file='.env')) as c:
 city=verify_city(GraphRepository(c,CITY_GRAPH),json.loads((root/'data/ingestion/city-v3.json').read_text()));assert city==old['city']
 controlled=capture(GraphRepository(c,old['controlled_source']['graph'])).fingerprint;assert controlled==old['controlled_source']
 clone=capture(GraphRepository(c,old['counterfactual_clone']['graph'])).fingerprint;assert clone==old['counterfactual_clone']
 probe=c.select_graph('civicly_b01_runtime').ro_query('MATCH (n:B01Probe {id:$id}) RETURN n.id,n.source_kind,n.task LIMIT 1',params={'id':'B01-PERSISTENCE'}).result_set;assert probe==old['original_b01_probe']
 status=MigrationRunner(c,'civicly_knowledge').status();assert status['ready']
 result={'status':'PASS','city':city,'controlled_source':controlled,'counterfactual_clone':clone,'original_b01_probe':probe,'canonical_migration':status}
args.output.write_text(json.dumps(result,indent=2)+'\n');print('Retained evidence and migration PASS')
