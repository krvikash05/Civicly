import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ApiClient } from '../lib/api/client.ts';
import { ApiError } from '../lib/api/errors.ts';
import { validSchema } from '../lib/api/validation.ts';
import { LatestRead } from '../lib/read/latest.ts';
import {
  metrics,
  parseIssue,
  issueName,
  displayStatus,
  displayTime,
  registeredCases,
  uniqueCaseForIncident,
  caseHref,
  loadSelectedCase,
} from '../lib/read/cases.ts';
import type { ApiModels } from '../lib/generated/models.ts';

const ok = (data: unknown) => Response.json({ data, request_id: 'test-req', schema_version: 1 });

test('metrics array defines exact four backend metrics with descriptions', () => {
  const fields = metrics.map(m => m.field);
  assert.deepEqual(fields, [
    'completed_work_orders',
    'verified_work_orders',
    'active_investigations',
    'pending_approvals',
  ]);
  assert.equal(metrics.find(m => m.field === 'completed_work_orders')?.description, 'Completion alone does not prove resolution');
  assert.equal(metrics.find(m => m.field === 'active_investigations')?.description, 'Excludes completed and cancelled cases');
});

test('issue parsing and naming handle valid and invalid values', () => {
  assert.equal(parseIssue('WATERLOGGING'), 'WATERLOGGING');
  assert.equal(parseIssue('ROAD_DAMAGE'), 'ROAD_DAMAGE');
  assert.equal(parseIssue('WASTE_ACCUMULATION'), 'WASTE_ACCUMULATION');
  assert.equal(parseIssue('INVALID_ISSUE'), undefined);
  assert.equal(parseIssue(null), undefined);

  assert.equal(issueName('WATERLOGGING'), 'Waterlogging');
  assert.equal(issueName('ROAD_DAMAGE'), 'Road damage');
  assert.equal(issueName('WASTE_ACCUMULATION'), 'Waste accumulation');
  assert.equal(issueName('UNKNOWN_TYPE'), 'unknown type');
});

test('displayStatus and displayTime formatting', () => {
  assert.equal(displayStatus('IN_PROGRESS'), 'in progress');
  assert.equal(displayStatus('ACTIVE'), 'active');
  assert.equal(displayStatus(null), 'Not recorded');
  assert.equal(displayStatus(undefined), 'Not recorded');

  assert.match(displayTime('2026-10-18T12:00:00Z'), /IST/);
  assert.equal(displayTime('not-a-date'), 'Date unavailable');
});

test('registeredCases filters out NOT_STARTED and filters by issue', () => {
  const sampleCatalog: ApiModels['ScenarioPage'] = {
    items: [
      {
        id: 'S01',
        title: 'Waterlogging Scenario',
        stage: 'BASELINE_VISIBLE',
        issue_types: ['WATERLOGGING'],
        next_operator_steps: [],
        limitations: [],
        cases: [
          {
            issue_type: 'WATERLOGGING',
            investigation_id: 'INV-01',
            incident_id: 'INC-01',
            cluster_id: 'CLU-01',
            asset_id: 'AST-01',
            department_id: 'DEPT-WATER',
          },
        ],
      },
      {
        id: 'S02',
        title: 'Road Damage Scenario',
        stage: 'NOT_STARTED',
        issue_types: ['ROAD_DAMAGE'],
        next_operator_steps: [],
        limitations: [],
        cases: [
          {
            issue_type: 'ROAD_DAMAGE',
            investigation_id: 'INV-02',
            incident_id: 'INC-02',
            cluster_id: 'CLU-02',
            asset_id: 'AST-02',
            department_id: 'DEPT-ROAD',
          },
        ],
      },
      {
        id: 'S03',
        title: 'Waste Accumulation Scenario',
        stage: 'EVIDENCE_REVEALED',
        issue_types: ['WASTE_ACCUMULATION'],
        next_operator_steps: [],
        limitations: [],
        cases: [
          {
            issue_type: 'WASTE_ACCUMULATION',
            investigation_id: 'INV-03',
            incident_id: 'INC-03',
            cluster_id: 'CLU-03',
            asset_id: 'AST-03',
            department_id: 'DEPT-WASTE',
          },
        ],
      },
    ],
    next_cursor: null,
    total_count: 3,
  };

  const allVisible = registeredCases(sampleCatalog);
  assert.equal(allVisible.length, 2);
  assert.equal(allVisible[0].investigation_id, 'INV-01');
  assert.equal(allVisible[1].investigation_id, 'INV-03');

  const waterOnly = registeredCases(sampleCatalog, 'WATERLOGGING');
  assert.equal(waterOnly.length, 1);
  assert.equal(waterOnly[0].incident_id, 'INC-01');

  const roadOnly = registeredCases(sampleCatalog, 'ROAD_DAMAGE');
  assert.equal(roadOnly.length, 0); // S02 is NOT_STARTED
});

test('uniqueCaseForIncident and caseHref', () => {
  const cases = [
    {
      scenarioId: 'S01',
      stage: 'BASELINE_VISIBLE',
      issue_type: 'WATERLOGGING' as const,
      investigation_id: 'INV-01',
      incident_id: 'INC-01',
      cluster_id: 'CLU-01',
      asset_id: 'AST-01',
      department_id: 'DEPT-01',
    },
  ];

  assert.equal(uniqueCaseForIncident(cases, 'INC-01')?.investigation_id, 'INV-01');
  assert.equal(uniqueCaseForIncident(cases, 'INC-99'), undefined);

  assert.equal(
    caseHref({ issue: 'WATERLOGGING', incident: 'INC-01', investigation: 'INV-01' }),
    '/investigations?issue=WATERLOGGING&incident=INC-01&investigation=INV-01#case-workspace'
  );
  assert.equal(caseHref({}), '/investigations#case-workspace');
  assert.equal(caseHref({investigation:'INV-01',section:'report'}),'/investigations?investigation=INV-01&section=report#case-workspace');
});

test('loadSelectedCase with investigation loads linked incidents', async () => {
  const mockInvestigation: ApiModels['InvestigationDTO'] = {
    id: 'INV-100',
    status: 'IN_PROGRESS',
    incident_ids: ['INC-100', 'INC-101'],
    historical_incident_ids: [],
    problem_cluster_id: 'CLU-100',
    active_hypothesis_ids: [],
    pending_inspection_ids: [],
    current_plan_id: null,
    graph_revision: 5,
    expected_hash: 'a'.repeat(64),
  };

  const mockIncidents: Record<string, ApiModels['IncidentDTO']> = {
    'INC-100': {
      id: 'INC-100',
      issue_type: 'WATERLOGGING',
      subtype: 'STREET_FLOODING',
      location_id: 'LOC-1',
      started_at: '2026-10-18T10:00:00Z',
      ended_at: null,
      status: 'ACTIVE',
      cluster_id: 'CLU-100',
      complaint_ids: [],
      expected_hash: 'b'.repeat(64),
    },
    'INC-101': {
      id: 'INC-101',
      issue_type: 'WATERLOGGING',
      subtype: 'STREET_FLOODING',
      location_id: 'LOC-2',
      started_at: '2026-10-18T11:00:00Z',
      ended_at: null,
      status: 'ACTIVE',
      cluster_id: 'CLU-100',
      complaint_ids: [],
      expected_hash: 'c'.repeat(64),
    },
  };

  const client = new ApiClient(async (path) => {
    if (path === '/api/v1/investigations/INV-100') return ok(mockInvestigation);
    if (path === '/api/v1/incidents/INC-100') return ok(mockIncidents['INC-100']);
    if (path === '/api/v1/incidents/INC-101') return ok(mockIncidents['INC-101']);
    return Response.json({ error: { code: 'NOT_FOUND', message: 'not found' } }, { status: 404 });
  });
  client.setSession('test-token');

  const res = await loadSelectedCase(client, { investigation: 'INV-100' });
  assert.equal(res.investigation?.id, 'INV-100');
  assert.equal(res.incidents.length, 2);
  assert.equal(res.incidents[0].id, 'INC-100');
  assert.equal(res.incidents[1].id, 'INC-101');

  // Matching with issue filter passes
  const withIssue = await loadSelectedCase(client, { investigation: 'INV-100', issue: 'WATERLOGGING' });
  assert.equal(withIssue.investigation?.id, 'INV-100');

  // Mismatched issue filter throws SELECTION_MISMATCH
  await assert.rejects(
    loadSelectedCase(client, { investigation: 'INV-100', issue: 'ROAD_DAMAGE' }),
    (err: unknown) => err instanceof ApiError && err.code === 'SELECTION_MISMATCH'
  );

  // Mismatched incident ID throws CONTRACT_MISMATCH
  await assert.rejects(
    loadSelectedCase(client, { investigation: 'INV-100', incident: 'INC-FOREIGN' }),
    (err: unknown) => err instanceof ApiError && err.code === 'CONTRACT_MISMATCH'
  );
});

test('loadSelectedCase with standalone incident', async () => {
  const mockIncident: ApiModels['IncidentDTO'] = {
    id: 'INC-200',
    issue_type: 'ROAD_DAMAGE',
    subtype: 'POTHOLE',
    location_id: 'LOC-5',
    started_at: '2026-10-18T09:00:00Z',
    ended_at: null,
    status: 'ACTIVE',
    cluster_id: null,
    complaint_ids: ['CMP-01'],
    expected_hash: 'd'.repeat(64),
  };

  const client = new ApiClient(async (path) => {
    if (path === '/api/v1/incidents/INC-200') return ok(mockIncident);
    return Response.json({ error: { code: 'NOT_FOUND', message: 'not found' } }, { status: 404 });
  });
  client.setSession('test-token');

  const res = await loadSelectedCase(client, { incident: 'INC-200' });
  assert.equal(res.investigation, null);
  assert.equal(res.incidents.length, 1);
  assert.equal(res.incidents[0].id, 'INC-200');

  // Matching issue
  const matching = await loadSelectedCase(client, { incident: 'INC-200', issue: 'ROAD_DAMAGE' });
  assert.equal(matching.incidents[0].id, 'INC-200');

  // Mismatching issue throws SELECTION_MISMATCH
  await assert.rejects(
    loadSelectedCase(client, { incident: 'INC-200', issue: 'WATERLOGGING' }),
    (err: unknown) => err instanceof ApiError && err.code === 'SELECTION_MISMATCH'
  );

  // Empty selection throws CLIENT_VALIDATION
  await assert.rejects(
    loadSelectedCase(client, {}),
    (err: unknown) => err instanceof ApiError && err.code === 'CLIENT_VALIDATION'
  );
});

test('LatestRead suppresses stale inflight reads', async () => {
  const read = new LatestRead<string>();
  const published: string[] = [];

  let resolveFirst!: (val: string) => void;
  const firstPromise = new Promise<string>(r => { resolveFirst = r; });

  // Start first read
  read.run(
    () => firstPromise,
    val => published.push(val),
    () => {}
  );

  // Start second read before first completes
  read.run(
    async () => 'second-result',
    val => published.push(val),
    () => {}
  );

  await new Promise(r => setTimeout(r, 10));

  // Now resolve first late
  resolveFirst('first-result');
  await new Promise(r => setTimeout(r, 10));

  // Only second-result should have published!
  assert.deepEqual(published, ['second-result']);
});

test('LatestRead cancel aborts controller', async () => {
  const read = new LatestRead<string>();
  let wasAborted = false;

  read.run(
    async (signal) => {
      signal.addEventListener('abort', () => { wasAborted = true; });
      await new Promise(r => setTimeout(r, 50));
      return 'done';
    },
    () => assert.fail('must not publish after cancel'),
    () => assert.fail('must not reject after cancel')
  );

  read.cancel();
  assert(wasAborted, 'signal should have been aborted');
});

test('DashboardSummary and Incident schemas validate valid objects', () => {
  const sampleSummary: ApiModels['DashboardSummary'] = {
    active_incidents: 5,
    active_clusters: 2,
    open_clusters: 2,
    active_investigations: 3,
    pending_approvals: 1,
    completed_work_orders: 4,
    verified_work_orders: 2,
    issue_counts: { WATERLOGGING: 2, ROAD_DAMAGE: 2, WASTE_ACCUMULATION: 1 },
    recurrence_counts: { WATERLOGGING: 1, ROAD_DAMAGE: 1, WASTE_ACCUMULATION: 0 },
    graph_revision: 42,
    as_of: '2026-10-18T12:00:00Z',
    definitions: ['Def 1', 'Def 2'],
    limitations: ['Lim 1'],
  };

  assert(validSchema('DashboardSummary', sampleSummary));
});
