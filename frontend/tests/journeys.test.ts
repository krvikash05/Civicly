import test from 'node:test';
import assert from 'node:assert/strict';
import Ajv from 'ajv';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import {
  groupJourneys,
  SUGGESTED_JOURNEY_ID,
  filterScenariosByCategory,
  formatStageName,
  getStageBadgeClass,
  getScenarioHref,
  getScenarioPrimaryCase,
  getScenarioIssueLabel,
} from '../lib/read/journeys.ts';
import {
  getOperatorProfile,
  isActionPermitted,
  MUNICIPAL_OPERATORS,
} from '../lib/read/roles.ts';
import type { ScenarioDTO } from '../lib/generated/models.ts';

test('filterScenariosByCategory filters correctly', () => {
  const sampleScenarios: ScenarioDTO[] = [
    {
      id: 'S01',
      title: 'Waterlogging at culvert',
      issue_types: ['WATERLOGGING'],
      stage: 'BASELINE_VISIBLE',
      cases: [
        {
          issue_type: 'WATERLOGGING',
          investigation_id: 'INV-01',
          incident_id: 'INC-01',
          cluster_id: 'CLUS-01',
          asset_id: 'DRAIN-01',
          department_id: 'DEPT-DRAIN',
        },
      ],
      next_operator_steps: ['Inspect culvert'],
      limitations: ['Synthetic telemetry'],
    },
    {
      id: 'S02',
      title: 'Pavement distress at MG Road',
      issue_types: ['ROAD_DAMAGE'],
      stage: 'PLAN_AND_APPROVAL',
      cases: [
        {
          issue_type: 'ROAD_DAMAGE',
          investigation_id: 'INV-02',
          incident_id: 'INC-02',
          cluster_id: 'CLUS-02',
          asset_id: 'ROAD-02',
          department_id: 'DEPT-ROAD',
        },
      ],
      next_operator_steps: ['Submit resurfacing plan'],
      limitations: [],
    },
    {
      id: 'S03',
      title: 'Water main pressure leak causing road collapse',
      issue_types: ['WATERLOGGING', 'ROAD_DAMAGE'],
      stage: 'EVIDENCE_REVEALED',
      cases: [
        {
          issue_type: 'WATERLOGGING',
          investigation_id: 'INV-03',
          incident_id: 'INC-03',
          cluster_id: 'CLUS-03',
          asset_id: 'PIPE-03',
          department_id: 'DEPT-WATER',
        },
      ],
      next_operator_steps: ['Cross-department coordination'],
      limitations: [],
    },
    {
      id: 'S04',
      title: 'Illegal garbage accumulation blocking drain',
      issue_types: ['WASTE_ACCUMULATION'],
      stage: 'FOLLOW_UP',
      cases: [
        {
          issue_type: 'WASTE_ACCUMULATION',
          investigation_id: 'INV-04',
          incident_id: 'INC-04',
          cluster_id: 'CLUS-04',
          asset_id: 'DUMP-04',
          department_id: 'DEPT-SAN',
        },
      ],
      next_operator_steps: ['Post-cleanup monitoring'],
      limitations: [],
    },
  ];

  // ALL returns all 4
  assert.equal(filterScenariosByCategory(sampleScenarios, 'ALL').length, 4);

  // WATERLOGGING returns S01 and S03 (cross-category)
  const water = filterScenariosByCategory(sampleScenarios, 'WATERLOGGING');
  assert.equal(water.length, 2);
  assert(water.some((s) => s.id === 'S01'));
  assert(water.some((s) => s.id === 'S03'));

  // ROAD_DAMAGE returns S02 and S03
  const road = filterScenariosByCategory(sampleScenarios, 'ROAD_DAMAGE');
  assert.equal(road.length, 2);
  assert(road.some((s) => s.id === 'S02'));
  assert(road.some((s) => s.id === 'S03'));

  // WASTE_ACCUMULATION returns S04
  const waste = filterScenariosByCategory(sampleScenarios, 'WASTE_ACCUMULATION');
  assert.equal(waste.length, 1);
  assert.equal(waste[0].id, 'S04');

  // CROSS_CATEGORY returns S03
  const cross = filterScenariosByCategory(sampleScenarios, 'CROSS_CATEGORY');
  assert.equal(cross.length, 1);
  assert.equal(cross[0].id, 'S03');
});

test('stage formatting and badges', () => {
  assert.equal(formatStageName('BASELINE_VISIBLE'), '1. Baseline Reports');
  assert.equal(formatStageName('EVIDENCE_REVEALED'), '2. Evidence & Hypotheses');
  assert.equal(formatStageName('PLAN_AND_APPROVAL'), '3. Plan & Approval');
  assert.equal(formatStageName('FOLLOW_UP'), '4. Post-Work Monitoring');
  assert.equal(formatStageName('NOT_STARTED'), 'Pending Activation');

  assert.equal(getStageBadgeClass('FOLLOW_UP'), 'badge badge-verified');
  assert.equal(getStageBadgeClass('PLAN_AND_APPROVAL'), 'badge badge-warning');
  assert.equal(getStageBadgeClass('EVIDENCE_REVEALED'), 'badge badge-active');
  assert.equal(getStageBadgeClass('BASELINE_VISIBLE'), 'badge badge-candidate');
});

test('getScenarioHref and primary case mapping', () => {
  const scenarioWithInv: ScenarioDTO = {
    id: 'S01',
    title: 'Test Scenario',
    issue_types: ['WATERLOGGING'],
    stage: 'BASELINE_VISIBLE',
    cases: [
      {
        issue_type: 'WATERLOGGING',
        investigation_id: 'INV-TEST-01',
        incident_id: 'INC-TEST-01',
        cluster_id: 'C-01',
        asset_id: 'A-01',
        department_id: 'DEPT-DRAIN',
      },
    ],
    next_operator_steps: [],
    limitations: [],
  };

  assert.equal(getScenarioHref(scenarioWithInv), '/investigations?investigation=INV-TEST-01&section=report');
  assert.equal(getScenarioPrimaryCase(scenarioWithInv)?.asset_id, 'A-01');
  assert.equal(getScenarioIssueLabel(scenarioWithInv), 'Waterlogging');

  const crossScenario: ScenarioDTO = {
    ...scenarioWithInv,
    id: 'S03',
    issue_types: ['WATERLOGGING', 'ROAD_DAMAGE'],
  };
  assert.equal(getScenarioIssueLabel(crossScenario), 'Cross-Category');
  // An uninitialized definition must not masquerade as an available journey.
  assert.equal(getScenarioHref({...scenarioWithInv, stage:'NOT_STARTED', cases:[]}), null);
});

test('municipal role governance and permission boundaries', () => {
  // OP-ANALYST profile check
  const analyst = getOperatorProfile('OP-ANALYST');
  assert.equal(analyst.role, 'ANALYST');
  assert.equal(analyst.departmentId, 'DEPT-COORD');
  assert(analyst.capabilities.length > 0);
  assert(analyst.boundaries.length > 0);

  // Separation of duties invariant: Analyst can draft/submit, but CANNOT self-approve
  assert.equal(isActionPermitted('ANALYST', 'DRAFT_PLAN'), true);
  assert.equal(isActionPermitted('ANALYST', 'SUBMIT_PLAN'), true);
  assert.equal(isActionPermitted('ANALYST', 'APPROVE_PLAN'), false); // Strictly prohibited
  assert.equal(isActionPermitted('ANALYST', 'DISPATCH_WORK'), false);
  assert.equal(isActionPermitted('ANALYST', 'RESET_DEMO'), false);

  // OP-APPROVER can approve plans, cannot draft
  assert.equal(isActionPermitted('APPROVER', 'APPROVE_PLAN'), true);
  assert.equal(isActionPermitted('APPROVER', 'DRAFT_PLAN'), false);
  assert.equal(isActionPermitted('APPROVER', 'RESET_DEMO'), false);

  // OP-ADMIN has elevated admin reset permissions
  assert.equal(isActionPermitted('ADMIN', 'RESET_DEMO'), true);
  assert.equal(isActionPermitted('ADMIN', 'APPROVE_PLAN'), true);

  // Department leads can dispatch work within their departmental scope
  assert.equal(isActionPermitted('DEPARTMENT_LEAD', 'DISPATCH_WORK'), true);
  assert.equal(isActionPermitted('DEPARTMENT_LEAD', 'APPROVE_PLAN'), false);

  // All 7 seeded operators defined
  assert.equal(Object.keys(MUNICIPAL_OPERATORS).length, 7);
  assert('OP-ANALYST' in MUNICIPAL_OPERATORS);
  assert('OP-APPROVER' in MUNICIPAL_OPERATORS);
  assert('OP-DRAIN-LEAD' in MUNICIPAL_OPERATORS);
  assert('OP-ROAD-LEAD' in MUNICIPAL_OPERATORS);
  assert('OP-WASTE-LEAD' in MUNICIPAL_OPERATORS);
  assert('OP-WATER-LEAD' in MUNICIPAL_OPERATORS);
  assert('OP-ADMIN' in MUNICIPAL_OPERATORS);
});

test('closed schema validation validates ScenarioDTO', () => {
  const root = resolve(import.meta.dirname, '../..');
  const schemaPath = resolve(root, 'contracts/api_models.json');
  const raw = JSON.parse(readFileSync(schemaPath, 'utf8'));

  const ajv = new Ajv({ strict: false, allErrors: true });
  for (const [key, value] of Object.entries(raw.$defs || {})) {
    ajv.addSchema(value as any, `#/$defs/${key}`);
  }

  const validateScenario = ajv.compile(raw.$defs.ScenarioDTO);

  const validScenario: ScenarioDTO = {
    id: 'S01',
    title: 'Ward 12 Culvert Waterlogging',
    issue_types: ['WATERLOGGING'],
    stage: 'BASELINE_VISIBLE',
    current_stage: 'BASELINE_VISIBLE',
    cases: [
      {
        issue_type: 'WATERLOGGING',
        investigation_id: 'INV-B09-01',
        incident_id: 'INC-B09-01',
        cluster_id: 'CLUS-B09-01',
        asset_id: 'DRAIN-101',
        department_id: 'DEPT-DRAIN',
        evidence_ids: ['EVID-01'],
        plan_id: null,
        work_order_id: null,
      },
    ],
    next_operator_steps: ['Dispatch field crew'],
    limitations: ['Synthetic district model'],
  };

  assert(validateScenario(validScenario), JSON.stringify(validateScenario.errors));

  // Closed schema check: extra properties must be rejected
  const invalidScenario = {
    ...validScenario,
    invented_field: 'illegal',
  };
  assert.equal(validateScenario(invalidScenario), false);
});

// F35: catalog definitions and partial progress cannot become completed journeys.
import type {DirectoryCase} from '../lib/read/workflow.ts';
const journey=(id:string,stage:string,issue_type='ROAD_DAMAGE'):DirectoryCase=>({investigation_id:id,incident_id:'INC-'+id,incident_ids:['INC-'+id],issue_type,stage});
test('curated journeys keep unfinished and cancelled cases separate; suggested case must actually be completed',()=>{
 const rows=[journey('OTHER','COMPLETED'),journey('OPEN','OPEN'),journey(SUGGESTED_JOURNEY_ID,'COMPLETED'),journey('MON','MONITORING'),journey('CANCEL','CANCELLED')];
 const groups=groupJourneys(rows,'ALL');assert.deepEqual(groups.completed.map(c=>c.investigation_id),[SUGGESTED_JOURNEY_ID,'OTHER']);
 assert.deepEqual(groups.ongoing.map(c=>c.investigation_id),['MON','OPEN']);assert.equal(groups.cancelled.length,1);
 assert.equal(groupJourneys([journey(SUGGESTED_JOURNEY_ID,'OPEN')],'ALL').completed.length,0);assert.equal(groupJourneys([],'ALL').completed.length,0);
});
test('curated category filters and deduplication preserve genuine multi-category investigations',()=>{
 const road=journey('CROSS','COMPLETED'),water=journey('CROSS','COMPLETED','WATERLOGGING');
 const rows=[road,road,water,journey('WASTE','MONITORING','WASTE_ACCUMULATION')];
 assert.equal(groupJourneys(rows,'ALL').completed.length,2);
 assert.equal(groupJourneys(rows,'CROSS_CATEGORY').completed.length,2);assert.equal(groupJourneys(rows,'CROSS_CATEGORY').ongoing.length,0);
 assert.equal(groupJourneys(rows,'WASTE_ACCUMULATION').ongoing.length,1);assert.equal(groupJourneys(rows,'ROAD_DAMAGE').completed.length,1);
});
test('scenario links begin at report and do not invent runs for empty definitions',()=>{
 const bare={id:'S12',cases:[],stage:'NOT_STARTED'} as unknown as ScenarioDTO;
 assert.equal(getScenarioHref(bare),null);
 assert.equal(getScenarioHref({...bare,cases:[{incident_id:'INC & /',investigation_id:''} as never]}),'/investigations?incident=INC%20%26%20%2F&section=report');
});
