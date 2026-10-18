"""Execution-policy/HTTP interception negatives; zero external provider calls."""
import asyncio,subprocess,sys,os,json
from pathlib import Path
import httpx,pytest
from app.agents.provider import Gemini,ProviderSettings,ProviderError
from app.agents.policy import Permit
from app.agents.spending import Ledger


def test_credential_presence_never_authorizes_live(monkeypatch):
    calls=[]
    async def post(*a,**kw):calls.append(1);raise AssertionError('Must not run')
    monkeypatch.setattr(httpx.AsyncClient,'post',post)
    with pytest.raises(ProviderError,match='LIVE_NOT_AUTHORIZED'):
        asyncio.run(Gemini(ProviderSettings(GEMINI_API_KEY='synthetic-test-key')).choose({},50000))
    assert calls==[]


def test_mock_permission_cannot_use_real_transport(tmp_path):
    model=Gemini(ProviderSettings(GEMINI_API_KEY='synthetic-test-key'),permit=Permit.mocked(),ledger=Ledger(tmp_path/'ledger'))
    with pytest.raises(ProviderError,match='MOCK_PERMIT_REQUIRES_MOCK_TRANSPORT'):asyncio.run(model.choose({},50000))


def test_ordinary_suite_denies_even_explicit_live_permit(tmp_path):
    p=Permit.explicit_live(approved=True,investigation_id='I',thread_id='T')
    model=Gemini(ProviderSettings(GEMINI_API_KEY='synthetic-test-key'),permit=p,ledger=Ledger(tmp_path/'ledger'))
    with pytest.raises(ProviderError,match='DISABLED_IN_ORDINARY_TESTS'):asyncio.run(model.choose({'state':{'investigation_id':'I','thread_id':'T'}},50000))


def test_http_interlock_blocks_before_network_in_parent_and_child(monkeypatch):
    monkeypatch.setenv('CIVICLY_GUARD_PROBE','1')
    async def probe():
        async with httpx.AsyncClient() as client:
            with pytest.raises(RuntimeError,match='HTTP_DISABLED'):await client.post('https://generativelanguage.googleapis.com/v1beta/models/fixture:generateContent')
    asyncio.run(probe())
    code="import os,httpx;os.environ['CIVICLY_GUARD_PROBE']='1';httpx.post('https://generativelanguage.googleapis.com/v1beta/models/fixture:generateContent')"
    p=subprocess.run([sys.executable,'-c',code],capture_output=True,env={'PYTHONPATH':str(Path('backend').absolute())})
    assert p.returncode!=0 and b'HTTP_DISABLED' in p.stderr


def test_opt_in_is_bound_to_particular_scope(monkeypatch):
    p=Permit.explicit_live(approved=True,investigation_id='I',thread_id='T')
    monkeypatch.delenv('CIVICLY_TEST_NO_LIVE')
    with pytest.raises(Exception,match='SCOPE_MISMATCH'):p.check(None,{'state':{'investigation_id':'OTHER','thread_id':'T'}})
    with pytest.raises(Exception,match='OPT_IN'):Permit.explicit_live(approved=False,investigation_id='I',thread_id='T')
