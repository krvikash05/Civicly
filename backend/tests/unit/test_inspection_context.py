"""Current inspection metadata cannot silently masquerade as causal evidence."""
from types import SimpleNamespace as N
import pytest
from app.agents.inspection_context import requested_inspections
from app.graph.repository import PreconditionFailed


def fixture(monkeypatch,*,scope='INV',status='COMPLETED',report_inspection='INS'):
 import app.agents.inspection_context as module
 report=N(id='REPORT',report=N(inspection_id=report_inspection,private_findings='not in metadata'))
 reader=N(node=lambda *a:N(properties={'status':status,'requested_at':'2026-10-18T12:00:00Z','completed_at':'2026-10-18T12:01:00Z'}),edges=lambda *a,**k:[N(target='REPORT')] if status=='COMPLETED' else [],evidence=lambda id:report)
 monkeypatch.setattr(module,'Reader',lambda *a:reader)
 service=N(repo=N(_read=lambda *a:[]),inspection_source=lambda *a:({'investigation_id':scope,'department_id':'DEPT-SAN'},{'W1'}))
 state=N(as_of='2026-10-18T13:00:00Z',investigation_id='INV',pending_inspections=['INS'],asset_ids=['W1'])
 return service,state


def test_completed_status_and_report_pointers_preserve_history_without_report_contents(monkeypatch):
 service,state=fixture(monkeypatch);rows=requested_inspections(service,state)
 assert rows[0]['status']=='COMPLETED' and rows[0]['report_evidence_ids']==['REPORT']
 assert rows[0]['metadata_only_not_causal_evidence'] is True
 assert 'private_findings' not in str(rows) and state.pending_inspections==['INS']


def test_pending_status_does_not_invent_a_report(monkeypatch):
 service,state=fixture(monkeypatch,status='PROPOSED')
 assert requested_inspections(service,state)[0]['report_evidence_ids']==[]

@pytest.mark.parametrize('change',[{'scope':'OTHER'},{'report_inspection':'OTHER'}])
def test_foreign_inspection_or_report_scope_rejected(monkeypatch,change):
 service,state=fixture(monkeypatch,**change)
 with pytest.raises(PreconditionFailed):requested_inspections(service,state)


def test_supplemental_scoped_inspection_discovered_without_mutating_pending(monkeypatch):
 service,state=fixture(monkeypatch);state.pending_inspections=[]
 service.repo._read=lambda *a:[['INS']]
 assert requested_inspections(service,state)[0]['report_evidence_ids']==['REPORT']
 assert state.pending_inspections==[]


def test_supplemental_foreign_investigation_is_not_exposed(monkeypatch):
 service,state=fixture(monkeypatch,scope='OTHER');state.pending_inspections=[]
 service.repo._read=lambda *a:[['INS']]
 assert requested_inspections(service,state)==[]


def test_supplemental_scan_overflow_fails_closed(monkeypatch):
 service,state=fixture(monkeypatch);service.repo._read=lambda *a:[[str(i)] for i in range(101)]
 with pytest.raises(PreconditionFailed,match='CAPACITY'):requested_inspections(service,state)
