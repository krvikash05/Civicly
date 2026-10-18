"""Actual SQLite history/migration/operator recovery; simulated usage only."""
import hashlib,json,sqlite3
from pathlib import Path
import pytest
from app.agents.spending import Ledger,Pricing,SpendError,dollars

USAGE={'promptTokenCount':100,'candidatesTokenCount':20,'thoughtsTokenCount':0,'totalTokenCount':120}

def hold(path):
    l=Ledger(path);l.configure_case('I');l.acquire('I','T','O');p=Pricing()
    l.reserve('R','I','T',p.data['model'],'B10-O-R',p.version,1000,'O')
    l.reconcile('R',p.actual(USAGE),USAGE);l.release('O');return l

def resolve(l,**changes):
    info=l.inspect_hold('R');args=dict(authorized=True,operator='synthetic-operator',reason='Verified exact usage/pricing and available caps',verified_pricing=Pricing().version,usage_sha256=hashlib.sha256(info['request']['usage'].encode()).hexdigest(),evidence_ref='SYNTHETIC-RECEIPT-1');args.update(changes);l.resolve_hold('R',**args)

def test_new_defaults_and_explicit_existing_config_upgrade(tmp_path):
    l=Ledger(tmp_path/'new');assert l.summary()['configuration']['project_cap']==dollars(8)
    l.configure_case('new');assert l.summary('new')['case_cap']==dollars('.50')
    old=Ledger(tmp_path/'old',project_limit=6,default_case_limit='.15');old.configure_case('old');old.acquire('old','T','O');old.reserve('U','old','T','gemini-3.8-flash','B10','old',1000,'O');old.release('O')
    assert Ledger(tmp_path/'old').summary('old')['case_cap']==dollars('.15')
    old.update_limits(reason='Operator explicitly authorized8/.50',project_limit=8,default_case_limit='.50',complex_case_limit='1.50')
    assert old.summary('old')['project_accounted']==1000 and old.summary('old')['case_cap']==dollars('.15')
    old.configure_case('complex','1.50')
    with pytest.raises(SpendError):old.configure_case('too-large','1.51')


def test_hold_recovers_after_reopen_without_changing_request(tmp_path):
    path=tmp_path/'l';l=hold(path);before=l.inspect_hold('R')['request'];resolve(Ledger(path));new=Ledger(path)
    assert new.inspect_hold('R')['request']==before and new.inspect_hold('R')['hold']['status']=='RESOLVED'
    new.acquire('I','T','N');new.reserve('NEXT','I','T','gemini-3.8-flash','B10-O-R','TEST',1000,'N')
    with new.db() as db:
        assert db.execute("SELECT count(*) FROM accounting_events WHERE operation='RESOLVE_HOLD'").fetchone()[0]==1
        with pytest.raises(sqlite3.IntegrityError,match='IMMUTABLE'):db.execute('DELETE FROM accounting_events')

@pytest.mark.parametrize('change',[{'authorized':False},{'reason':''},{'usage_sha256':'bad'},{'verified_pricing':'wrong'}])
def test_no_unbound_hold_clear(tmp_path,change):
    l=hold(tmp_path/'l')
    with pytest.raises(SpendError):resolve(l,**change)
    assert l.summary()['holds']


def test_unresolved_billing_cannot_clear_and_caps_rechecked(tmp_path):
    l=hold(tmp_path/'l');l.configure_case('I','.50')
    with l.db() as db:db.execute("UPDATE cases SET cap=1 WHERE id='I'") # Deliberate stale-cap fault.
    with pytest.raises(SpendError,match='CAP_RECONCILIATION'):resolve(l)
    l.configure_case('I','.50');resolve(l)
    l.acquire('I','T','O');l.reserve('U','I','T','gemini-3.8-flash','B10','TEST',1000,'O');l.reconcile('U',None,{});l.release('O')
    with l.db() as db:db.execute("INSERT INTO request_holds VALUES('U','Uncertain billing','OPEN',0)")
    with pytest.raises(SpendError,match='BILLING_UNRESOLVED'):l.resolve_hold('U',authorized=True,operator='op',reason='cannot clear',verified_pricing='TEST',usage_sha256='?',evidence_ref='?')


def test_legacy_hold_mapping_is_repeatable_and_non_destructive(tmp_path):
    path=tmp_path/'l';l=hold(path)
    with l.db() as db:
        db.execute('DROP TABLE request_holds');db.execute('DROP TABLE legacy_hold_links');db.execute("INSERT INTO holds VALUES(1,'Original overage')")
    reopened=Ledger(path);assert len(reopened.summary()['holds'])==1
    with reopened.db() as db:assert db.execute('SELECT reason FROM holds').fetchone()[0]=='Original overage'
    resolve(reopened);assert not Ledger(path).summary()['holds']


def test_exact_hold_resolution_in_fresh_operator_process(tmp_path):
    import os,subprocess,sys
    path=tmp_path/'ledger';l=hold(path);before=l.inspect_hold('R')['request']
    proc=subprocess.run([sys.executable,'-m','app.agents.spending','--ledger',str(path),'resolve-hold','R','--operator','synthetic-restarted-operator','--reason','Verified simulated receipt after restart','--verified-pricing',Pricing().version,'--usage-sha256',hashlib.sha256(before['usage'].encode()).hexdigest(),'--evidence-ref','SIMULATED-RECEIPT','--authorize'],env={**os.environ,'PYTHONPATH':'backend'},capture_output=True,text=True,timeout=15)
    assert proc.returncode==0 and json.loads(proc.stdout)['hold']['status']=='RESOLVED'
    reopened=Ledger(path);assert not reopened.summary()['holds'] and reopened.inspect_hold('R')['request']==before
    with reopened.db() as db:assert db.execute("SELECT operator FROM accounting_events WHERE operation='RESOLVE_HOLD'").fetchone()[0]=='synthetic-restarted-operator'


def test_configuration_history_cannot_be_rewritten(tmp_path):
    l=Ledger(tmp_path/'ledger');l.update_limits(reason='Reviewed allocation',project_limit=8,default_case_limit='.50')
    with l.db() as db:
        for sql in ['DELETE FROM config_changes',"UPDATE config_changes SET reason='rewritten'"]:
            with pytest.raises(sqlite3.IntegrityError,match='IMMUTABLE'):db.execute(sql)
