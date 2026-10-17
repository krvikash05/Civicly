"""Retained operator B09 demo: authored reports, revisions and read-only persistence."""
import argparse
import json
import re
from pathlib import Path
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.graph.analysis.counterfactual import capture
from app.services.evidence import EvidenceService
from tests.b09_fixtures import create, open_case, propose, report, assess


def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['create', 'verify'])
    p.add_argument('--proof', type=Path, required=True)
    p.add_argument('--output', type=Path)
    p.add_argument('--lifecycle-log', type=Path)
    args = p.parse_args()
    with connect(Settings(_env_file='.env')) as db:
        if args.action == 'create':
            if args.proof.exists():
                raise ValueError('Refuse to overwrite retained proof')
            f = create(db, retain_source=True)
            inv = open_case(f)
            h = propose(f, inv)
            alternative = propose(f, inv, cause='CAPACITY_DEFICIT', ref='capacity-alternative')
            a, b = report(f, inv, 'first'), report(f, inv, 'second')
            first = assess(f, h, [a.entity_id, b.entity_id], ref='verified')
            old_hash = f.repo.get_node(first.entity_id).content_hash
            counter = report(f, inv, 'third', ['DRAIN_CLEAR', 'CAPACITY_TEST_EXCEEDED'])
            corrected = assess(f, h, ref='corrected')  # Discovery preserves omitted counterevidence.
            competing = assess(f, alternative, ref='competing')
            assert first.assessment.assessment == 'VERIFIED'
            assert corrected.assessment.assessment == 'INCONCLUSIVE'
            assert competing.assessment.assessment == 'SUPPORTED'
            assert f.repo.get_node(first.entity_id).content_hash == old_hash
            history = f.service.history(h, f.clock())
            value = {'status': 'PASS', 'evidence_class': 'REAL_FALKORDB_AUTHORED_SYNTHETIC_RETAINED_B09_FIXTURE',
                'graph': f.repo.graph.name, 'source_B08_graph': f.source_graph, 'source_B08_fingerprint': f.source_fingerprint,
                'actual_B08_ids': {k: {'incident_id': v.incident_id, 'cluster_id': v.cluster_id} for k, v in f.receipts.items()},
                'investigation_id': inv, 'hypothesis_id': h, 'alternative_id': alternative,
                'verified': first.model_dump(mode='json'), 'corrected': corrected.model_dump(mode='json'),
                'competing': competing.model_dump(mode='json'), 'history': [a.model_dump(mode='json') for a in history],
                'as_of': f.clock(), 'fingerprint': capture(f.repo).fingerprint,
                'schema': 'Unchanged registryv3/0001', 'canonical_promotion': False,
                'lifecycle': 'Not yet tested for this retained graph; verify after real regression lifecycle'}
            args.proof.write_text(json.dumps(value, indent=2) + '\n')
        else:
            value = json.loads(args.proof.read_text())
            r = GraphRepository(db, value['graph'])
            assert capture(r).fingerprint == value['fingerprint']
            assert capture(GraphRepository(db, value['source_B08_graph'])).fingerprint == value['source_B08_fingerprint']
            assert [a.model_dump(mode='json') for a in EvidenceService(r).history(value['hypothesis_id'], value['as_of'])] == value['history']
            if args.lifecycle_log:
                log = args.lifecycle_log.read_text()
                assert 'after restart (same container)' in log and 'after recreation (different container, retained volume)' in log
                assert re.search(r'=+ \d+ passed in [\d.]+s', log) and 'failed,' not in log
            assert args.output
            args.output.write_text(json.dumps({'status': 'PASS', 'graph': r.graph.name,
                'fingerprint': capture(r).fingerprint, 'B08_source_unchanged': True,
                'immutable_history_preserved': True, 'domain_mutated_by_verifier': False,
                'real_lifecycle_log': str(args.lifecycle_log) if args.lifecycle_log else None}, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'action': args.action}))


if __name__ == '__main__':
    main()
