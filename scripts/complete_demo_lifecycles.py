"""Operator-assisted completion of two exact human-approved retained demo plans.

No model call, scenario reset or automatic retry. Authenticated domain APIs own
all state transitions. A persisted dispatch marker forbids blindly rerunning any
mutation, including after an uncertain HTTP response. Field observations are
explicitly synthetic and independently reviewed by the analyst identity.
"""
import argparse
import json
import os
from pathlib import Path

from app.graph.schema import utc_now
from exact_road_lifecycle import Journey

PROOF = Path('docs/evidence/DEMO-LIFECYCLE-COMPLETION')
PRIVATE = Path('.runtime/demo-presenter/run-01/lifecycle-completion')
APPROVED = {
    'water': {
        'case': 'INV-B09-8b006fb97aa2b908fc69addcf7ecd037',
        'plan': 'PLAN-B12-da6d426cc7a42982a3dac6c8a76af2a6',
        'hash': '1b04b300f41379529bd0e7b6667bf28c1fbaaec5f1bbe38f4cfb5803a3a74286',
        'action': 'DRAIN_BLOCKAGE_CLEARANCE', 'target': 'DRAIN-101',
        'who': 'OP-DRAIN-LEAD', 'department': 'DEPT-DRAIN',
        'followup': ['COMPARABLE_FOLLOWUP_RAINFALL', 'FOLLOWUP_WATERLOGGING'],
    },
    'road': {
        'case': 'INV-B09-f663f7a1473c4a28a941d147633e08ad',
        'plan': 'PLAN-B12-3a26fd93b1eb567bf101905dc4c43b76',
        'hash': 'a39f811a8913ba4c5870a6acff9a05b918027db1768c64146e32bc4f90a2c834',
        'action': 'SUBGRADE_REPAIR', 'target': 'ROAD-DEMO-SUBGRADE-02',
        'who': 'OP-ROAD-LEAD', 'department': 'DEPT-ROAD',
        'followup': ['WEAR_EXPOSURE', 'FOLLOWUP_PAVEMENT'],
    },
}


def immutable_json(path, value, private=False):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700 if private else 0o755)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600 if private else 0o644)
    with os.fdopen(fd, 'w') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


class Completion(Journey):
    def __init__(self, name, retry_unstarted_approval=False):
        super().__init__()
        self.name = name
        self.scope = APPROVED[name]
        self.retry_unstarted_approval = retry_unstarted_approval

    def prove_unstarted_approval(self, marker, key):
        """Explicit operator retry, only for the reproduced pre-intent failure."""
        if self.name != 'water' or key != 'approve-v1' or not self.retry_unstarted_approval:
            raise RuntimeError('PRIOR_DISPATCH_REQUIRES_OPERATOR_REVIEW')
        from app.config import Settings
        from app.graph.connection import connect
        from app.graph.repository import GraphRepository
        from app.active import active_scope, load
        from app.events.store import Store
        from app.services.http.service import request_identity
        from app.graph.models import digest
        profile = load(self.config.profile)
        request = request_identity(profile.graph, 'OP-APPROVER',
                                   'EXACT-ROAD-LIFECYCLE-COMPLETION-water-approve-v1')
        original = json.loads(marker.read_text())
        # The API persists its intent before dispatch. No intent, unchanged
        # original approval and no orders for this plan prove this request did
        # not dispatch, even after separately authorized road-case writes.
        approval_id = original['path'].split('/')[2]
        approval = super().call('GET', '/approvals/' + approval_id, who='OP-APPROVER')
        plan = super().call('GET', '/plans/' + self.scope['plan'])
        orders = super().call('GET', '/work-orders?limit=50')['items']
        if (approval['status'] != 'PENDING' or approval['expected_hash'] != original['request']['expected_hash']
                or plan['status'] != 'PENDING_APPROVAL' or plan['content_hash'] != self.scope['hash']
                or any(w['plan_id'] == self.scope['plan'] for w in orders)):
            raise RuntimeError('ORIGINAL_PENDING_APPROVAL_AND_NO_WORK_REQUIRED')
        with connect(Settings(_env_file='.env')) as db, active_scope(profile):
            repo = GraphRepository(db, profile.graph)
            revision = repo._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.repo_revision,coalesce(m.repo_pending,'')")
            intent = Store(repo, utc_now).get('api_request', request)
            if len(revision) != 1 or revision[0][1] or intent is not None:
                raise RuntimeError('CLEAN_SOURCE_AND_ABSENT_REQUEST_NOT_PROVEN')
        if original['request']['plan_hash'] != self.scope['hash']:
            raise RuntimeError('ORIGINAL_APPROVAL_PAYLOAD_CHANGED')
        attempt = 1 + len(list(PRIVATE.glob('water-approve-v1-manual-prewrite-retry*-dispatch.json')))
        if attempt > 2:
            raise RuntimeError('BOUNDED_OPERATOR_RETRY_EXHAUSTED')
        immutable_json(PROOF / ('water-prewrite-reconciliation-' + str(attempt) + '.json'), {
            'at': utc_now(), 'request_id': request, 'source': profile.graph,
            'source_revision': revision, 'api_intent': None,
            'original_dispatch_hash': digest(original),
            'original_approval_unchanged': True, 'plan_orders': 0,
            'reason': 'Original503 occurred before API intent; no pending write; original approval hash unchanged, exact plan pending and no work orders. Bounded explicit same-key operator dispatch; no uncertain write or quarantine cleared.'})
        return marker.with_name('water-approve-v1-manual-prewrite-retry-' + str(attempt) + '-dispatch.json')

    def call(self, method, path, body=None, who='OP-ANALYST', key=None, review=False):
        if method != 'GET':
            if not key:
                raise RuntimeError('MUTATION_KEY_REQUIRED')
            marker = PRIVATE / (self.name + '-' + key + '-dispatch.json')
            if marker.exists():
                marker = self.prove_unstarted_approval(marker, key)
            immutable_json(marker, {'at': utc_now(), 'method': method, 'path': path,
                                    'operator': who, 'request': body, 'key': key}, True)
        result = super().call(method, path, body, who,
                              'LIFECYCLE-COMPLETION-' + self.name + '-' + key if key else None, review)
        if method != 'GET':
            immutable_json(marker.with_name(marker.stem + '-receipt.json'), result, True)
        return result

    def execute(self):
        s = self.scope
        plan = self.call('GET', '/plans/' + s['plan'])
        if (plan['version'] != 1 or plan['content_hash'] != s['hash'] or
                plan['status'] != 'PENDING_APPROVAL' or plan['investigation_id'] != s['case']):
            raise RuntimeError('EXACT_APPROVED_PENDING_PLAN_REQUIRED')
        tasks = plan['task_bindings']
        if len(tasks) != 1:
            raise RuntimeError('EXACT_SINGLE_TASK_REQUIRED')
        task = tasks[0]
        if (task['action_type'] != s['action'] or task['target_ids'] != [s['target']] or
                task['department_id'] != s['department'] or task['eligible_assignee_ids'] != [s['who']]):
            raise RuntimeError('HUMAN_APPROVED_ASSIGNMENT_CHANGED')
        binding = {'plan_id': s['plan'], 'plan_version': 1, 'plan_hash': s['hash'],
                   'assignments': [{k: task[k] for k in ['task_id', 'action_type', 'target_ids', 'department_id']}
                                   | {'assignee_id': s['who']}]}
        approvals = self.call('GET', '/approvals?limit=50&status=PENDING', who='OP-APPROVER')['items']
        candidates = [a for a in approvals if a['plan_id'] == s['plan']]
        if len(candidates) != 1:
            raise RuntimeError('ONE_EXACT_PENDING_APPROVAL_REQUIRED')
        a = candidates[0]
        approval = self.call('POST', '/approvals/' + a['id'] + '/decision', {
            **binding, 'expected_hash': a['expected_hash'], 'decision': 'APPROVED',
            'reason': 'Human explicitly approved both exact simulated plans and work/follow-up in Codex on 2026-10-19; preserve AI recommendation and evidence.'
        }, who='OP-APPROVER', key='approve-v1')
        order = self.call('POST', '/work-orders', {**binding, 'approval_id': a['id'],
                          'task_id': task['task_id']}, who='OP-APPROVER', key='order-v1')
        wid = order['id']

        def current():
            return self.call('GET', '/work-orders/' + wid)

        self.call('POST', '/work-orders/' + wid + '/status', {
            'expected_hash': current()['expected_hash'], 'new_status': 'ASSIGNED',
            'reason': 'Assign exact human-approved simulated task to responsible lead'
        }, who=s['who'], key='assign')
        self.call('POST', '/work-orders/' + wid + '/progress', {
            'expected_hash': current()['expected_hash'], 'action': 'START',
            'reason': 'Begin authorized synthetic demo work after service prerequisite checks', 'evidence_ids': []
        }, who=s['who'], key='start')

        def report(purpose, codes):
            def command(command, step, reviewed=False):
                body = {'expected_hash': current()['expected_hash'], 'purpose': purpose, 'command': command}
                if reviewed:
                    body['review_reason'] = 'Independent authenticated analyst review of explicitly synthetic demo observations; no actual municipal field work claimed'
                return self.call('POST', '/work-orders/' + wid + '/inspections', body,
                                 who=s['who'], key=purpose + '-' + step, review=reviewed)['status']
            iid = command({'operation': 'request_inspection', 'investigation_id': s['case'],
                           'asset_ids': [s['target']], 'department_id': s['department'],
                           'inspection_type': 'B14_FOLLOWUP' if purpose == 'FOLLOWUP' else s['action']}, 'request')
            for status in ['REQUESTED', 'SCHEDULED', 'IN_PROGRESS']:
                ins = self.call('GET', '/inspections/' + iid)
                command({'operation': 'transition_inspection', 'inspection_id': iid,
                         'expected_hash': ins['expected_hash'], 'status': status,
                         **({'scheduled_at': utc_now()} if status == 'SCHEDULED' else {})}, status)
            ins = self.call('GET', '/inspections/' + iid)
            observed_at = utc_now()
            observations = [{'asset_id': s['target'], 'code': code,
                             'statement': 'Explicit synthetic demonstration observation ' + code + '; operator-assisted simulation, not real field execution',
                             'method': 'DIRECT_SYNTHETIC_FIELD_TEST', 'observed_at': observed_at,
                             'result': 'OBSERVED', 'value': 0.0 if code.startswith('FOLLOWUP_') else None,
                             'unit': 'boolean' if code.startswith('FOLLOWUP_') else None} for code in codes]
            eid = command({'operation': 'report_inspection', 'inspection_id': iid,
                           'expected_hash': ins['expected_hash'], 'source_id': 'DEMO-LIFECYCLE-' + self.name + '-' + purpose,
                           'record_id': iid, 'source_kind': 'SYNTHETIC', 'observations': observations}, 'report', True)
            return {'inspection_id': iid, 'evidence_id': eid, 'observations': observations}

        completion = report('COMPLETION', ['ACTION_COMPLETED'])
        self.call('POST', '/work-orders/' + wid + '/progress', {
            'expected_hash': current()['expected_hash'], 'action': 'COMPLETE',
            'reason': 'Reviewed synthetic completion; independent follow-up still required',
            'evidence_ids': [completion['evidence_id']]
        }, who=s['who'], key='complete')
        monitoring = {'plan': self.call('GET', '/plans/' + s['plan']),
                      'investigation': self.call('GET', '/investigations/' + s['case']), 'order': current()}
        immutable_json(PROOF / (self.name + '-monitoring.json'), monitoring)
        if monitoring['plan']['status'] != 'MONITORING' or monitoring['order']['status'] != 'COMPLETED':
            raise RuntimeError('COMPLETION_MUST_NOT_SKIP_MONITORING')
        start = utc_now()
        followup = report('FOLLOWUP', s['followup'])
        end = utc_now()
        outcome = self.call('POST', '/work-orders/' + wid + '/outcomes', {
            'expected_hash': current()['expected_hash'], 'evidence_ids': [followup['evidence_id']],
            'window_start': start, 'window_end': end
        }, key='evaluate')
        immutable_json(PROOF / (self.name + '-execution.json'), {
            'mode': 'HUMAN_APPROVED_OPERATOR_ASSISTED_SYNTHETIC_WORK_NO_NEW_MODEL_RUN',
            'binding': binding, 'approval': approval, 'order_id': wid, 'completion': completion,
            'followup': followup, 'outcome': outcome, 'calls': self.calls})
        if outcome['assessment_status'] != 'RESOLUTION_VERIFIED' or not outcome['case_closed']:
            raise RuntimeError('INDEPENDENT_OUTCOME_DID_NOT_CLOSE_CASE')
        return self.verify()

    def verify(self):
        s = self.scope
        inv = self.call('GET', '/investigations/' + s['case'])
        plan = self.call('GET', '/plans/' + s['plan'])
        approvals = self.call('GET', '/approvals?limit=50', who='OP-APPROVER')['items']
        approval = next(a for a in approvals if a['plan_id'] == s['plan'])
        orders = [w for w in self.call('GET', '/work-orders?limit=50')['items'] if w['plan_id'] == s['plan']]
        incidents = [self.call('GET', '/incidents/' + i) for i in inv['historical_incident_ids'] + inv['incident_ids']]
        memory = [self.call('GET', '/cases/' + i['id'] + '/memory') for i in incidents]
        outcomes = self.call('GET', '/problem-clusters/' + inv['problem_cluster_id'] + '/outcomes')
        graph = self.call('GET', '/investigations/' + s['case'] + '/graph?depth=4&include_candidates=true')
        trace = self.call('GET', '/investigations/' + s['case'] + '/trace')
        if not (inv['status'] == plan['status'] == 'COMPLETED' and approval['status'] == 'APPROVED'
                and len(orders) == 1 and orders[0]['status'] == 'COMPLETED'
                and any(m['items'] for m in memory)
                and any(o['case_closed'] and o['work_order_id'] == orders[0]['id'] for o in outcomes['items'])):
            raise RuntimeError('PERSISTED_COMPLETE_WORKFLOW_NOT_ESTABLISHED')
        result = {'investigation': inv, 'plan': plan, 'approval': approval, 'orders': orders,
                  'incidents': incidents, 'memory': memory, 'outcomes': outcomes, 'graph': graph,
                  'trace': trace, 'provider_requests_initiated': 0}
        immutable_json(PROOF / (self.name + '-verified-' + utc_now().replace(':', '').replace('.', '') + '.json'), result)
        return {'case': s['case'], 'plan': s['plan'], 'status': inv['status'],
                'approval': approval['status'], 'orders': len(orders), 'memory_items': sum(len(m['items']) for m in memory)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['execute', 'verify'])
    parser.add_argument('--case', choices=APPROVED, required=True)
    parser.add_argument('--retry-unstarted-approval', action='store_true',
                        help='Explicit bounded operator retry of original water approval only after absent-intent, unchanged-approval and no-work proof')
    args = parser.parse_args()
    journey = Completion(args.case, args.retry_unstarted_approval)
    try:
        print(json.dumps(journey.execute() if args.operation == 'execute' else journey.verify(), indent=2))
    finally:
        journey.close()


if __name__ == '__main__':
    main()
