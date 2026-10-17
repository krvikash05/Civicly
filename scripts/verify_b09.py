"""Read-only predecessor preservation, including accepted B08 traces/intake graph."""
import argparse
import json
import subprocess
from pathlib import Path
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.graph.analysis.counterfactual import capture
from app.mcp.civicly.runtime import connections
from app.mcp.civicly.storage import TraceStore
from app.mcp.civicly.models import TraceRecord
from app.graph.models import digest

ROOT = Path(__file__).resolve().parents[1]


def accepted(name):
    return json.loads(subprocess.check_output(['git', 'show', 'HEAD:docs/evidence/' + name], cwd=ROOT))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--b08-anchor', type=Path, default=ROOT / 'docs/evidence/B09-B08-after-lifecycle.json')
    args = p.parse_args()
    previous = args.output.with_name(args.output.stem + '-B01-B07.json')
    subprocess.run([str(ROOT / 'backend/.venv/bin/python'), str(ROOT / 'scripts/verify_b08.py'), '--output', str(previous)], cwd=ROOT, check=True)
    value = json.loads(previous.read_text())
    with connect(Settings(_env_file='.env')) as db:
        b08 = accepted('B08-retained-proof.json')
        anchor = json.loads(args.b08_anchor.read_text())['after_retry']
        current = capture(GraphRepository(db, b08['graph'])).fingerprint
        assert current == anchor
    verified = 0
    with connections() as (_, writer, name):
        store = TraceStore(writer, name)
        for record in accepted('B08-city-mcp-proof.json')['persisted_server_traces']:
            assert store.get(record['context']['execution_id']) == TraceRecord.model_validate_json(json.dumps(record))
            verified += 1
        results = list(accepted('B08-B07R-regression-proof.json')['results'].values())
        results.append(accepted('B08-runtime-proof.json')['examples']['actual-mcp-fixture-source']['result']['result'])
        for result in results:
            record = store.get(result['execution_id'])
            assert record.output_sha256 == digest(result) and record.source_evidence_ids == result['source_evidence_ids']
            verified += 1
    value.update({'accepted_B08_traces_verified': verified, 'accepted_B08_intake_fingerprint': current,
                  'total_accepted_trace_observations_verified': verified + value['accepted_trace_records_verified']})
    args.output.write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'accepted_B08_traces_verified': verified, 'B08_domain_unchanged': True}))


if __name__ == '__main__':
    main()
