"""Real private SQLite transactions; all costs simulated, no Gemini network."""
import json,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
import pytest
from app.agents.spending import Ledger,Pricing,SpendError,dollars


def ready(path,project=6,cap='.15',maximum=1):
    l=Ledger(path,project_limit=project,default_case_limit=cap,max_concurrent=maximum)
    l.configure_case('I');l.acquire('I','T','O');return l

def reserve(l,id='R',amount='.10',owner='O'):
    l.reserve(id,'I','T','gemini-3.8-flash','B10-O','TEST-PRICING',dollars(amount),owner)

def test_usage_prices_separate_input_output_thinking_and_cached():
    p=Pricing();u={'promptTokenCount':100,'candidatesTokenCount':20,'thoughtsTokenCount':30,'totalTokenCount':150,'cachedContentTokenCount':20}
    assert p.actual(u)==80*750+20*75+20*3750+30*3750
    assert p.actual({'totalTokenCount':150}) is None
    with pytest.raises(SpendError,match='PRICING_EXPIRED'):Pricing(clock=lambda:datetime(2027,1,1,tzinfo=timezone.utc)).validate('gemini-3.8-flash')
    with pytest.raises(SpendError,match='UNSUPPORTED'):p.validate('unverified-model')

def test_cap_retains_unknown_billing_and_reconciles_exactly(tmp_path):
    l=ready(tmp_path/'ledger');reserve(l);l.reconcile('R',None,{},'NETWORK_TIMEOUT')
    with pytest.raises(SpendError,match='INVESTIGATION'):reserve(l,'R2')
    assert l.summary('I')['case_accounted']==dollars('.10')
    l.reconcile('R',dollars('.01'),{'verified_test_usage':True})
    reserve(l,'R2');assert l.summary('I')['case_accounted']==dollars('.11')
    l.reconcile('R',dollars('.01'),{'verified_test_usage':True})
    with pytest.raises(SpendError,match='CONFLICT'):l.reconcile('R',0,{})
    with pytest.raises(SpendError,match='ALREADY_RESERVED'):reserve(l,'R')
    assert l.summary()['warnings']

def test_default_concurrency_and_restart_durable_uncertainty(tmp_path):
    path=tmp_path/'ledger';l=ready(path);reserve(l)
    with pytest.raises(SpendError,match='CONCURRENCY'):l.acquire('I','OTHER','SECOND')
    restored=Ledger(path)
    assert restored.summary('I')['uncertain_requests']==1
    with pytest.raises(SpendError,match='CONCURRENCY'):restored.acquire('I','T','NEW_PROCESS')
    restored.release('O');restored.acquire('I','T','NEW_PROCESS')
    assert restored.summary('I')['case_accounted']==dollars('.10')
    assert path.stat().st_mode&0o077==0

def test_explicit_case_increase_does_not_reset_cost(tmp_path):
    l=ready(tmp_path/'ledger');reserve(l);l.configure_case('I','.30');reserve(l,'R2')
    assert l.summary('I')['case_accounted']==dollars('.20')
    with pytest.raises(SpendError,match='EXPLICIT_INCREASE'):l.configure_case('I','.05')


def test_atomic_project_reservations_from_two_python_processes(tmp_path):
    path=tmp_path/'ledger';l=ready(path,project='.15',maximum=2);l.acquire('I','T','B')
    code='''import sys,time\nfrom pathlib import Path\nfrom app.agents.spending import Ledger,SpendError,dollars\np,owner,gate=sys.argv[1:]\nl=Ledger(p,project_limit='.15',max_concurrent=2)\nPath(gate+'.'+owner).touch()\nwhile not Path(gate).exists():time.sleep(.01)\ntry:l.reserve(owner,'I','T','gemini-3.8-flash','B10-O','TEST',dollars('.10'),owner)\nexcept SpendError:sys.exit(2)\n'''
    gate=tmp_path/'GO';processes=[subprocess.Popen([sys.executable,'-c',code,str(path),owner,str(gate)]) for owner in ['O','B']]
    try:
        deadline=time.monotonic()+15
        while not all(Path(str(gate)+'.'+o).exists() for o in ['O','B']):
            assert time.monotonic()<deadline;time.sleep(.02)
        gate.touch();assert sorted(p.wait(timeout=15) for p in processes)==[0,2]
        assert l.summary('I')['project_accounted']==dollars('.10')
    finally:
        for p in processes:
            if p.poll() is None:p.kill();p.wait()


def test_over_reservation_records_actual_cost_and_halts_future_calls(tmp_path):
    l=ready(tmp_path/'ledger');reserve(l,amount='.01');l.reconcile('R',dollars('.02'),{'simulated':True})
    assert l.summary('I')['case_accounted']==dollars('.02') and l.summary()['holds']
    with pytest.raises(SpendError,match='RECONCILIATION_REQUIRED'):reserve(l,'NEXT',amount='.01')


def test_operator_configuration_is_durable_and_audited(tmp_path):
    l=Ledger(tmp_path/'ledger');l.update_limits(project_limit=5,default_case_limit='.10',reason='Synthetic approved lower development allocation')
    assert Ledger(tmp_path/'ledger').summary()['project_cap']==dollars(5)
    with l.db() as db:assert db.execute('SELECT count(*) FROM config_changes').fetchone()[0]==1
