"""Pure rule-v2 tests; real persisted decisions are tested separately."""
import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from app.services.evidence.models import Assessment, Receipt, Journal, ReportInspection, IncidentAttribution
from app.services.evidence.policies import classify_reviewed


@pytest.mark.parametrize('rs,us,rc,uc,complete,label', [
    (False, False, False, False, False, 'INCONCLUSIVE'),
    (False, True, False, False, False, 'POSSIBLE'),
    (True, False, False, False, False, 'SUPPORTED'),
    (True, False, False, False, True, 'VERIFIED'),
    (False, False, True, False, False, 'CONTRADICTED'),
    (False, False, False, True, False, 'INCONCLUSIVE'),
    (True, False, False, True, True, 'INCONCLUSIVE'),
    (True, False, True, False, True, 'INCONCLUSIVE'),
    (False, True, True, False, False, 'INCONCLUSIVE'),
    (False, True, False, True, False, 'INCONCLUSIVE'),
    (False, False, True, True, False, 'CONTRADICTED'),
])
def test_authority_and_conflict_matrix(rs, us, rc, uc, complete, label):
    assert classify_reviewed(reviewed_support=rs, unreviewed_support=us, reviewed_contradiction=rc,
                             unreviewed_contradiction=uc, sufficient=complete) == label


def test_actual_accepted_v1_receipts_assessments_and_journal_shapes_stay_unchanged():
    proof = json.loads(Path('docs/evidence/B09-retained-proof.json').read_text())
    for name in ['verified', 'corrected', 'competing']:
        raw = proof[name]
        assert Receipt.model_validate_json(json.dumps(raw)).model_dump(mode='json') == raw
        old = raw['assessment']
        decoded = Assessment.model_validate_json(json.dumps(old))
        assert decoded.format_version == decoded.rule_version == 1 and decoded.classification is None
        assert decoded.model_dump(mode='json') == old
    # Original no-attribution report commands must retain the original hash input.
    command = {'operation':'report_inspection','request_id':'original','inspection_id':'I','expected_hash':'a'*64,
               'source_id':'S','record_id':'R','source_kind':'SYNTHETIC','observations':[
                   {'asset_id':'D','code':'C','statement':'Original','method':'DIRECT','observed_at':'2026-10-18T12:00:00Z',
                    'result':'OBSERVED','value':None,'unit':None}], 'review':None}
    assert ReportInspection.model_validate_json(json.dumps(command)).model_dump(mode='json') == command


@pytest.mark.parametrize('changes', [
    {'mode':'RETROSPECTIVE'}, {'basis_evidence_ids':['E']}, {'incident_ids':['I','I']},
    {'mode':'RETROSPECTIVE','basis_evidence_ids':['E','E']}, {'tenant_id':'x'},
])
def test_explicit_attribution_strictness(changes):
    with pytest.raises(ValidationError):
        IncidentAttribution.model_validate({'incident_ids':['I'],'rationale':'Source-specific relevance',**changes})


def test_v1_cannot_silently_be_relabeled_as_v2():
    old=json.loads(Path('docs/evidence/B09-retained-proof.json').read_text())['verified']['assessment']
    with pytest.raises(ValidationError):
        Assessment.model_validate_json(json.dumps({**old,'format_version':2,'rule_version':2}))


def test_legacy_classifier_entry_point_cannot_authorize_unreviewed_rejection():
    from app.services.evidence.policies import classify
    assert classify(support=False, contradiction=True, reviewed=False, sufficient=False)=='INCONCLUSIVE'
