"""Pure B09 schema/policy tests. No DB/MCP or model execution claimed here."""
import json
import math
import pytest
from pydantic import ValidationError
from app.services.evidence.models import parse_command, Actor, Review, Observation, Journal
from app.services.evidence.policies import classify, POLICIES

BASE = {'operation': 'open', 'request_id': 'open', 'incident_ids': ['I'], 'cluster_id': 'C'}


def test_strict_open_and_canonical_distinct_references():
    q = parse_command({**BASE, 'incident_ids': ['Z', 'A']})
    assert q.incident_ids == ['A', 'Z']


@pytest.mark.parametrize('changes', [{'tenant_id': 'demo-city'}, {'graph': 'other'}, {'unknown': 1},
    {'request_id': ''}, {'incident_ids': []}, {'incident_ids': ['I', 'I']}, {'cluster_id': 1},
    {'incident_ids': ['I'] * 4}, {'priority': 'SEVERE'}, {'operation': 'raw_cypher'}, {'request_id': True}])
def test_invalid_commands_rejected(changes):
    with pytest.raises((ValidationError, ValueError)):
        parse_command({**BASE, **changes})


@pytest.mark.parametrize('time', ['2026-10-18', '2026-10-18T12:00:00', '2026-99-18T12:00:00Z', '2026-10-18T12:00:00+00:00'])
def test_canonical_utc_boundary(time):
    with pytest.raises(ValidationError):
        parse_command({'operation': 'assess', 'request_id': 'a', 'hypothesis_id': 'h', 'expected_hash': 'a' * 64, 'as_of': time})


@pytest.mark.parametrize('changes', [{'value': True, 'unit': 'cm'}, {'value': '2', 'unit': 'cm'}, {'value': math.inf, 'unit': 'cm'}, {'value': 2}, {'unit': 'cm'}, {'result': 'VERIFIED'}, {'confidence': .9}])
def test_observation_strictness(changes):
    with pytest.raises(ValidationError):
        Observation(asset_id='D', code='DIRECT_TEST', statement='Synthetic observation', method='TEST', observed_at='2026-10-18T12:00:00Z', **changes)


@pytest.mark.parametrize('support,contra,reviewed,sufficient,label', [(False, False, False, False, 'INCONCLUSIVE'),
    (True, False, False, False, 'POSSIBLE'), (True, False, True, False, 'SUPPORTED'),
    (True, False, True, True, 'VERIFIED'), (True, True, True, True, 'INCONCLUSIVE'), (False, True, True, False, 'CONTRADICTED')])
def test_deterministic_vocabulary(support, contra, reviewed, sufficient, label):
    assert classify(support=support, contradiction=contra, reviewed=reviewed, sufficient=sufficient) == label


def test_three_issues_have_nonempty_discriminating_policies():
    assert set(POLICIES) == {'WATERLOGGING', 'ROAD_DAMAGE', 'WASTE_ACCUMULATION'}
    for rules in POLICIES.values():
        for rule in rules.values():
            assert len(rule['confirming']) >= 2 and rule['falsifying']
            assert not set(rule['confirming']) & set(rule['falsifying'])


def test_no_agent_or_unreviewed_review_context():
    for role in ['AGENT', 'DEPARTMENT_LEAD', 'APPROVER']:
        with pytest.raises(ValidationError):
            Review(reviewer_id='reviewer', role=role, reviewed=True, reason='review')
    with pytest.raises(ValidationError):
        Review(reviewer_id='reviewer', role='ANALYST', reviewed=False, reason='review')


def test_request_byte_budget():
    with pytest.raises(ValueError):
        parse_command({**BASE, 'request_id': 'x' * 33000})


def test_expected_confirming_and_falsifying_are_disjoint():
    with pytest.raises(ValidationError):
        parse_command({'operation': 'propose', 'request_id': 'p', 'investigation_id': 'inv', 'incident_ids': ['i'], 'asset_ids': ['a'],
            'cause_code': 'TEST', 'statement': 'Test', 'mechanism': 'Test', 'confirming_codes': ['SAME'], 'falsifying_codes': ['SAME']})


@pytest.mark.parametrize('value', [1, 1.0, 'true'])
def test_review_cannot_coerce_nonboolean(value):
    with pytest.raises(ValidationError):
        Review(reviewer_id='r', role='ANALYST', reviewed=value, reason='Test')


def test_machine_contract_matches_actual_models_and_criteria():
    from pathlib import Path
    from app.services.evidence.models import COMMAND, Receipt, Assessment, Report, InspectionView
    contract = json.loads(Path('contracts/evidence_hypotheses.json').read_text())
    assert contract['schemas']['command'] == COMMAND.json_schema()
    for model in [Actor, Review, Receipt, Assessment, Report, InspectionView]:
        assert contract['schemas'][model.__name__] == model.model_json_schema()
    assert contract['domain_criteria'] == POLICIES
