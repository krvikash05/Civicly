"""Typed/operator authority boundaries; no real DB or live-model claim."""
import pytest
from app.services.responsibility.models import Submission,Review
from app.services.responsibility.service import authorization,identity
from app.services.evidence.models import Actor
from app.services.operations.auth import Denied
from app.graph.repository import interval,intersection
BASE={'asset_id':'DRAIN-101','department_id':'DEPT-DRAIN','source_id':'synthetic-inventory','source_record_id':'row1','observed_at':'2026-10-18T10:00:00Z','valid_from':'2026-10-19T00:00:00Z'}
@pytest.mark.parametrize('extra',[{'reliability':'VERIFIED'},{'association_status':'VERIFIED'},{'source_kind':'MUNICIPAL'},{'reviewed_by':'OP-ADMIN'},{'graph':'civicly_knowledge'},{'source_version':True},{'observed_at':'2026-10-20T00:00:00Z'},{'valid_to':'2026-10-18T00:00:00Z'}])
def test_closed_submission_and_chronology(extra):
 with pytest.raises(ValueError):Submission.model_validate({**BASE,**extra})
@pytest.mark.parametrize('extra',[{'reviewed':False},{'reviewed':1},{'reviewed_by':'OP-ANALYST'},{'expected_hash':'invalid'},{'reason':''}])
def test_explicit_review_and_cas(extra):
 with pytest.raises(ValueError):Review.model_validate({'expected_hash':'a'*64,'reviewed':True,'reason':'Independent synthetic inventory review',**extra})
@pytest.mark.parametrize('role,department,operation,submitter',[('ADMIN','DEPT-COORD','submit',None),('ANALYST','DEPT-COORD','submit',None),('DEPARTMENT_LEAD','DEPT-ROAD','submit',None),('DEPARTMENT_LEAD','DEPT-DRAIN','review','OTHER'),('APPROVER','DEPT-COORD','review','OTHER'),('ADMIN','DEPT-COORD','review','OTHER'),('ANALYST','DEPT-COORD','review','SELF')])
def test_role_scope_and_independence(role,department,operation,submitter):
 with pytest.raises(Denied):authorization(Actor(id='SELF',role=role,department_id=department),operation,'DEPT-DRAIN',submitter)
def test_valid_authority_and_stable_scoped_source_identity():
 authorization(Actor(id='LEAD',role='DEPARTMENT_LEAD',department_id='DEPT-DRAIN'),'submit','DEPT-DRAIN')
 authorization(Actor(id='ANALYST',role='ANALYST'),'review',submitted_by='LEAD')
 a=Submission.model_validate(BASE);b=Submission.model_validate({**BASE,'observed_at':'2026-10-18T10:00:00.000000Z'})
 assert a==b and identity('graph-a',a)==identity('graph-a',b)!=identity('graph-b',b)
def test_verified_intervals_overlap_but_adjacent_history_is_distinct():
 a=interval({'valid_from':'2026-10-19T00:00:00Z','valid_to':'2026-10-20T00:00:00Z'})
 assert intersection(a,interval({'valid_from':'2026-10-19T12:00:00Z'})) is not None
 assert intersection(a,interval({'valid_from':'2026-10-20T00:00:00Z'})) is None

def test_service_rejects_unknown_operation_before_any_auth_or_dispatch():
 from app.services.responsibility.service import Responsibility
 from app.graph.repository import PreconditionFailed
 service=object.__new__(Responsibility)
 with pytest.raises(PreconditionFailed,match='CLOSED_OPERATION'):service.prepare('delete',None,{},None)

def test_required_existing_operations_migration_not_bypassed(monkeypatch):
 from types import SimpleNamespace
 from app.services.responsibility.service import Responsibility
 from app.graph.repository import PreconditionFailed
 import app.services.operations.migration as migration
 monkeypatch.setattr(migration,'OperationsMigration',lambda *a:SimpleNamespace(status=lambda:{'ready':False}))
 with pytest.raises(PreconditionFailed,match='0005_REQUIRED'):Responsibility(SimpleNamespace(client=None,graph=SimpleNamespace(name='SOURCE')),None)

@pytest.mark.parametrize('rows,verified_only,expected',[
 ([('CANDIDATE','DEPT-DRAIN'),('VERIFIED','DEPT-DRAIN')],False,['DEPT-DRAIN']),
 ([('CANDIDATE','DEPT-ROAD'),('VERIFIED','DEPT-DRAIN')],False,['DEPT-DRAIN']),
 ([('VERIFIED','DEPT-DRAIN'),('VERIFIED','DEPT-DRAIN')],False,[]),
 ([('CANDIDATE','DEPT-DRAIN')],True,[]),
 ([('CANDIDATE','DEPT-DRAIN')],False,['DEPT-DRAIN']),
])
def test_read_projection_prioritizes_single_verified_source_without_hiding_claims(monkeypatch,rows,verified_only,expected):
 # Unit source/visibility dependencies are explicit stubs; real projection is in journey.
 from types import SimpleNamespace
 from app.services.http.reads import Reads,Reader
 read=object.__new__(Reads);read.clock=lambda:'2026-10-19T12:00:00Z'
 read.repo=SimpleNamespace(_check_evidence=lambda p:None)
 read.edges=lambda *a,**kw:[SimpleNamespace(target=dept,properties={'association_status':status,'source_evidence_id':'EV'}) for status,dept in rows]
 monkeypatch.setattr(Reader,'node',lambda *a,**kw:None)
 assert read.ownership_departments('ASSET',verified_only=verified_only)==expected
