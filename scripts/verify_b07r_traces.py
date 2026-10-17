"""Fresh read-only comparison of accepted and corrective MCP trace observations."""
import json
from pathlib import Path
from app.mcp.civicly.runtime import connections
from app.mcp.civicly.storage import TraceStore
from app.mcp.civicly.models import TraceRecord
from app.mcp.civicly.contracts import digest

ROOT=Path(__file__).resolve().parents[1]
accepted=json.loads((ROOT/'docs/evidence/B07-runtime-proof.json').read_text())
before=json.loads((ROOT/'docs/evidence/B07R-before-outputs.json').read_text())
corrected=json.loads((ROOT/'docs/evidence/B07R-runtime-proof.json').read_text())
log=(ROOT/'docs/evidence/B07R-regression-tests.txt').read_text()
assert log.index('test_absent_work_order_keeps_explicit_operational_gaps PASSED')<log.index('after restart (same container)')<log.index('after recreation (different container, retained volume)')
with connections() as (_,writer,name):
    store=TraceStore(writer,name)
    for saved in accepted['persisted_server_traces']:
        assert store.get(saved['context']['execution_id'])==TraceRecord.model_validate_json(json.dumps(saved))
    for report in (before,corrected):
        for result in report['results'].values():
            record=store.get(result['execution_id'])
            assert record and record.validated_output and record.output_sha256==digest(result)
            assert record.source_evidence_ids==result['source_evidence_ids']
report={'status':'PASS','accepted_b07_server_records_unchanged':len(accepted['persisted_server_traces']),
        'precorrection_records_preserved_across_lifecycle':len(before['results']),
        'corrected_fixture_records_preserved_across_lifecycle':len(corrected['results']),
        'note':'Actual full-suite log verifies corrected fixture calls preceded successful restart and recreation; fresh readback verifies preservation.',
        'output_hashes_and_evidence_references_verified':True,'credential_values_logged':False}
(ROOT/'docs/evidence/B07R-trace-continuity.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
