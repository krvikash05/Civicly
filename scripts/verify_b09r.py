"""Read-only post-lifecycle verification of the isolated real v1->v2 correction."""
import argparse
from datetime import timedelta
import json
import subprocess
from pathlib import Path
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.graph.analysis.counterfactual import capture
from app.graph.schema import timestamp
from app.services.evidence import EvidenceService
from app.services.evidence.models import Receipt
from app.graph.models import digest
from app.mcp.civicly.runtime import connections
from app.mcp.civicly.storage import TraceStore
from app.mcp.civicly.models import TraceRecord


def accepted_trace_observations():
    def accepted(name):
        return json.loads(subprocess.check_output(['git','show','688b893:docs/evidence/'+name]))
    city=accepted('B09-city-mcp-proof.json')
    checked=0
    with connections() as (_,writer,name):
        store=TraceStore(writer,name)
        for value in city['persisted_server_traces']:
            assert store.get(value['context']['execution_id'])==TraceRecord.model_validate_json(json.dumps(value))
            checked+=1
        outputs=[*city['results'],city['exploratory'],*city['typed_dependencies'].values()]
        outputs.append(accepted('B09-runtime-proof.json')['examples']['actual-mcp']['values']['result'])
        for output in outputs:
            value=store.get(output['execution_id'])
            assert value.output_sha256==digest(output) and value.source_evidence_ids==output['source_evidence_ids']
            checked+=1
    return checked


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    old=json.loads(Path('docs/evidence/B09R-v1-proof.json').read_text())
    runtime=json.loads(Path('docs/evidence/B09R-runtime-proof.json').read_text())['results']['v1-to-v2-append']
    with connect(Settings(_env_file='.env')) as db:
        repo=GraphRepository(db,old['graph'])
        before=capture(repo).fingerprint
        assert before==runtime['graph_fingerprint']
        assert capture(GraphRepository(db,old['source_graph'])).fingerprint==old['source_fingerprint']
        service=EvidenceService(repo)
        legacy=Receipt.model_validate_json(json.dumps(old['v1_receipt']))
        assert service.readback(legacy).model_dump(mode='json')==old['v1_receipt']
        corrected=Receipt.model_validate_json(json.dumps(runtime['receipt']))
        assert service.readback(corrected,replayed=corrected.replayed)==corrected
        at=(timestamp(old['correction_as_of'])+timedelta(seconds=100)).isoformat().replace('+00:00','Z')
        history=service.history(old['hypothesis_id'],at)
        assert [(a.format_version,a.assessment) for a in history]==[(1,'CONTRADICTED'),(2,'INCONCLUSIVE')]
        assert history[1].previous_assessment_id==history[0].id
        assert repo.get_node(legacy.entity_id).content_hash==old['v1_assessment_node_hash']
        assert repo.get_node(legacy.journal_id).content_hash==old['v1_journal_node_hash']
        assert capture(repo).fingerprint==before
        result={'status':'PASS','domain_mutated_by_verifier':False,'graph':repo.graph.name,
                'fingerprint':before,'matches_pre_lifecycle_test_snapshot':True,'source_B08_unchanged':True,
                'v1_assessment_hash_unchanged':old['v1_assessment_node_hash'],
                'v1_journal_hash_unchanged':old['v1_journal_node_hash'],
                'v1_receipt_readback_exact':True,'v2_receipt_readback_exact':True,
                'history':[a.model_dump(mode='json') for a in history]}
    result['accepted_B09_trace_observations_verified']=accepted_trace_observations()
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='history'}))


if __name__=='__main__':main()
