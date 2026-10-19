"""Nonbillable public HTTPS acceptance; no domain writes or provider requests."""
import argparse
import json
from pathlib import Path

import httpx

CASES = {
    'water': 'INV-B09-8b006fb97aa2b908fc69addcf7ecd037',
    'road': 'INV-B09-f663f7a1473c4a28a941d147633e08ad',
    'original_road': 'INV-B09-b9d4d66e130ed348c4f6a50e9d66a891',
    'waste': 'INV-B09-95e00a75e74b708c966db68bc595dca0',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='https://civicly-13-55-205-208.sslip.io')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    url = args.url.rstrip('/')
    checks = []
    with httpx.Client(base_url=url, timeout=60) as client:
        home = client.get('/')
        assert home.status_code == 200
        checks.append({'check': 'public_https_homepage', 'pass': True})
        assert client.post('/api/demo-session', headers={'Origin': 'https://example.invalid'}).status_code == 403
        assert client.get('/api/v1/auth/me').status_code == 401
        checks.append({'check': 'cross_origin_and_unauthenticated_denials', 'pass': True})
        response = client.post('/api/demo-session', headers={'Origin': url})
        response.raise_for_status()
        token = response.json()['data']['access_token']
        headers = {'Authorization': 'Bearer ' + token, 'Origin': url}

        def get(path, auth=headers):
            response = client.get('/api/v1' + path, headers=auth)
            response.raise_for_status()
            return response.json()['data']

        try:
            ready = get('/health/ready')
            assert ready['status'] == 'ok' and all(v == 'ready' for v in ready['dependencies'].values())
            dashboard = get('/dashboard/summary')
            assert dashboard['pending_approvals'] == 0 and dashboard['completed_work_orders'] == 6
            assert dashboard['verified_work_orders'] == 3 and dashboard['active_investigations'] == 4
            orders = get('/work-orders?limit=50')['items']
            cases = []
            for name, case_id in CASES.items():
                inv = get('/investigations/' + case_id)
                trace = get('/investigations/' + case_id + '/trace')
                assert not trace['recovery_required']
                if name == 'waste':
                    assert inv['status'] == 'MONITORING' and trace['pause_reason'] == 'TOKEN_BUDGET'
                    assert inv['current_plan_id'] == 'PLAN-B12-d6664bb9cca6231ad5391e433ab5f39a'
                    plan = get('/plans/' + inv['current_plan_id'])
                    assert plan['status'] == 'MONITORING'
                    assert plan['content_hash'] == 'ffa5dfa47fce1cfc43d348c2076cb88485decbe09e887cf01442516f8b762140'
                    work = [w for w in orders if w['plan_id'] == plan['plan_id']]
                    assert len(work) == 1 and work[0]['status'] == 'COMPLETED'
                    outcomes = get('/problem-clusters/' + inv['problem_cluster_id'] + '/outcomes')['items']
                    assert any(o['work_order_id'] == work[0]['id'] for o in outcomes)
                    assert all(not o['case_closed'] for o in outcomes if o['work_order_id'] == work[0]['id'])
                    graph = get('/investigations/' + case_id + '/graph?depth=4&include_candidates=true')
                    assert any(n['id'] == work[0]['id'] for n in graph['nodes'])
                    cases.append({'case': case_id, 'status': inv['status'], 'saved_agent_pause': trace['pause_reason'],
                                  'plan': plan['plan_id'], 'work_orders': 1, 'case_closed': False,
                                  'graph_nodes': len(graph['nodes'])})
                    continue
                assert inv['status'] == 'COMPLETED'
                plan = get('/plans/' + inv['current_plan_id'])
                assert plan['status'] == 'COMPLETED'
                work = [w for w in orders if w['plan_id'] == plan['plan_id']]
                assert len(work) == (3 if name == 'original_road' else 1)
                assert all(w['status'] == 'COMPLETED' for w in work)
                incidents = inv['historical_incident_ids'] + inv['incident_ids']
                assert incidents
                memories = [get('/cases/' + i + '/memory') for i in incidents]
                assert any(m['items'] for m in memories)
                outcomes = get('/problem-clusters/' + inv['problem_cluster_id'] + '/outcomes')['items']
                assert any(o['case_closed'] and o['work_order_id'] in {w['id'] for w in work} for o in outcomes)
                graph = get('/investigations/' + case_id + '/graph?depth=4&include_candidates=true')
                assert any(n['kind'] == 'WorkOrder' for n in graph['nodes'])
                cases.append({'case': case_id, 'status': inv['status'], 'plan': plan['plan_id'],
                              'work_orders': len(work), 'memory_items': sum(len(m['items']) for m in memories),
                              'graph_nodes': len(graph['nodes']), 'trace_steps': len(trace['items'])})
            for case_id in ['INV-B09-917765cbf8fef632bd0459640c64f26f',
                            'INV-B09-9d231c8718136a90974e19c6c9a77c47',
                            'INV-B09-a2fe3dbdecd03984033026c4d0856295']:
                assert get('/investigations/' + case_id + '/trace')['recovery_required']
            checks.append({'check': 'three_completed_cases_waste_monitoring_and_quarantines', 'pass': True})
            procedures = get('/procedures?limit=50')
            assert procedures['items']
            with client.stream('GET', '/api/v1/events/stream', headers=headers, timeout=30) as stream:
                stream.raise_for_status()
                assert 'text/event-stream' in stream.headers['content-type']
                line = next((line for line in stream.iter_lines() if line), '')
                assert line
            checks.append({'check': 'authenticated_sse_frame', 'pass': True})
            result = {'status': 'PASS', 'url': url, 'checks': checks, 'dashboard': dashboard,
                      'dependencies': ready['dependencies'], 'cases': cases,
                      'provider_requests_initiated': 0, 'domain_writes': 0}
        finally:
            client.post('/api/v1/auth/logout', headers=headers, json={}).raise_for_status()
        assert client.get('/api/v1/auth/me', headers=headers).status_code == 401
        checks.append({'check': 'revoked_session_denied', 'pass': True})
    with args.output.open('x') as output:
        output.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'completed_cases': 3, 'monitoring_cases': 1, 'completed_work_orders': 6,
                      'pending_approvals': 0, 'url': url}))


if __name__ == '__main__':
    main()
