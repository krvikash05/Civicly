from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def pytest_addoption(parser):
    parser.addoption(
        "--run-persistence", action="store_true", default=False,
        help="Restart and recreate only this project's civicly FalkorDB container",
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-persistence"):
        for item in items:
            if "persistence" in item.keywords:
                item.add_marker(pytest.mark.skip(reason="Use --run-persistence to authorize lifecycle checks"))


def pytest_configure(config):
    """Normal tests are offline for Gemini even when .env credentials exist."""
    import os,sys,json
    guard=ROOT/'backend/test_guards'
    sys.path.insert(0,str(guard))
    config._civicly_guard_log=Path(os.environ.get('CIVICLY_TEST_REQUEST_LOG','/tmp/civicly-b10o-provider-requests.jsonl'))
    config._civicly_guard_log.write_text('')
    config._civicly_guard_log.chmod(0o600)
    os.environ['CIVICLY_TEST_NO_LIVE']='1'
    os.environ['CIVICLY_REQUEST_AUDIT_FILE']=str(config._civicly_guard_log)
    from civicly_no_live import install
    install()


def pytest_ignore_collect(collection_path,config):
    # Billable tests have a separate operator CLI entry; normal pytest never collects them.
    return 'live' in collection_path.parts and str(ROOT/'backend/tests/live') in str(collection_path)


def pytest_sessionfinish(session,exitstatus):
    import json
    path=session.config._civicly_guard_log
    events=[json.loads(line) for line in path.read_text().splitlines() if line]
    proof={'scope':'Entire ordinary pytest invocation and inherited Python children','exitstatus':int(exitstatus),
        'external_gemini_requests_sent':0,'blocked_attempts':len(events),'negative_interception_probes':sum(e['negative_probe'] for e in events),
        'ordinary_unexpected_attempts':sum(not e['negative_probe'] for e in events),'events':events,
        'mock_transport_calls':'Explicit MOCK_HTTP permits; not external requests or billed usage'}
    path.with_suffix('.json').write_text(json.dumps(proof,indent=2)+'\n')
    if proof['ordinary_unexpected_attempts']:
        session.exitstatus=pytest.ExitCode.TESTS_FAILED
