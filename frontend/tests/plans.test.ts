import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import Ajv from 'ajv';
import {
  computeTaskDag,
  formatShortHash,
  getStatusBadgeStyle,
} from '../lib/read/plans.ts';
import type { TaskDraft, PlanTaskBinding, PlanDTO, WorkOrderDTO } from '../lib/generated/models.ts';

test('computeTaskDag empty inputs return empty structure', () => {
  const result = computeTaskDag([], []);
  assert.equal(result.totalTasks, 0);
  assert.equal(result.nodes.length, 0);
  assert.equal(result.tiers.length, 0);
  assert.equal(result.hasCycle, false);
});

test('computeTaskDag linear dependency chain orders tiers sequentially', () => {
  const tasks: TaskDraft[] = [
    {
      id: 'TASK-C',
      action_type: 'SUBGRADE_REPAIR',
      target_ids: ['ROAD-1'],
      department_id: 'DEPT-ROAD',
      priority: 'MODERATE',
      prerequisites: [],
      depends_on: ['TASK-B'],
      evidence_ids: [],
      assessment_ids: [],
      procedure_citation: {} as any,
      expected_outcome: 'Repaved',
      verification_criteria: 'Smooth',
      risks: [],
    },
    {
      id: 'TASK-A',
      action_type: 'INSPECTION',
      target_ids: ['ROAD-1'],
      department_id: 'DEPT-ROAD',
      priority: 'HIGH',
      prerequisites: [],
      depends_on: [],
      evidence_ids: [],
      assessment_ids: [],
      procedure_citation: {} as any,
      expected_outcome: 'Subgrade opened',
      verification_criteria: 'Depth verified',
      risks: [],
    },
    {
      id: 'TASK-B',
      action_type: 'SUBGRADE_REPAIR',
      target_ids: ['ROAD-1'],
      department_id: 'DEPT-ROAD',
      priority: 'HIGH',
      prerequisites: [],
      depends_on: ['TASK-A'],
      evidence_ids: [],
      assessment_ids: [],
      procedure_citation: {} as any,
      expected_outcome: 'Compacted',
      verification_criteria: 'Density test pass',
      risks: [],
    },
  ];

  const dag = computeTaskDag(tasks);
  assert.equal(dag.totalTasks, 3);
  assert.equal(dag.hasCycle, false);
  assert.equal(dag.tiers.length, 3);

  // Tier 0 should be TASK-A
  assert.equal(dag.tiers[0].length, 1);
  assert.equal(dag.tiers[0][0].id, 'TASK-A');
  assert.equal(dag.tiers[0][0].tier, 0);

  // Tier 1 should be TASK-B
  assert.equal(dag.tiers[1].length, 1);
  assert.equal(dag.tiers[1][0].id, 'TASK-B');
  assert.equal(dag.tiers[1][0].tier, 1);

  // Tier 2 should be TASK-C
  assert.equal(dag.tiers[2].length, 1);
  assert.equal(dag.tiers[2][0].id, 'TASK-C');
  assert.equal(dag.tiers[2][0].tier, 2);
});

test('computeTaskDag diamond dependency graph parallelizes independent branches', () => {
  // A -> B, A -> C; then B -> D, C -> D
  const tasks: TaskDraft[] = [
    {
      id: 'TASK-ROOT',
      action_type: 'INSPECTION',
      target_ids: ['SITE-1'],
      department_id: 'DEPT-TRAFFIC',
      priority: 'CRITICAL',
      prerequisites: [],
      depends_on: [],
      evidence_ids: [],
      assessment_ids: [],
      procedure_citation: {} as any,
      expected_outcome: 'Perimeter secured',
      verification_criteria: 'Signage placed',
      risks: [],
    },
    {
      id: 'TASK-DRAIN',
      action_type: 'DRAIN_BLOCKAGE_CLEARANCE',
      target_ids: ['DRAIN-1'],
      department_id: 'DEPT-DRAIN',
      priority: 'HIGH',
      prerequisites: [],
      depends_on: ['TASK-ROOT'],
      evidence_ids: [],
      assessment_ids: [],
      procedure_citation: {} as any,
      expected_outcome: 'Inlet cleared',
      verification_criteria: 'Flow restored',
      risks: [],
    },
    {
      id: 'TASK-CULVERT',
      action_type: 'DRAIN_BLOCKAGE_CLEARANCE',
      target_ids: ['CULVERT-1'],
      department_id: 'DEPT-DRAIN',
      priority: 'HIGH',
      prerequisites: [],
      depends_on: ['TASK-ROOT'],
      evidence_ids: [],
      assessment_ids: [],
      procedure_citation: {} as any,
      expected_outcome: 'Barrel cleared',
      verification_criteria: 'Debris removed',
      risks: [],
    },
    {
      id: 'TASK-FINAL-CHECK',
      action_type: 'INSPECTION',
      target_ids: ['SITE-1'],
      department_id: 'DEPT-DRAIN',
      priority: 'MODERATE',
      prerequisites: [],
      depends_on: ['TASK-DRAIN', 'TASK-CULVERT'],
      evidence_ids: [],
      assessment_ids: [],
      procedure_citation: {} as any,
      expected_outcome: 'Site cleared',
      verification_criteria: 'Checklist signed',
      risks: [],
    },
  ];

  const dag = computeTaskDag(tasks);
  assert.equal(dag.totalTasks, 4);
  assert.equal(dag.hasCycle, false);
  assert.equal(dag.tiers.length, 3);

  // Tier 0: Root
  assert.equal(dag.tiers[0].length, 1);
  assert.equal(dag.tiers[0][0].id, 'TASK-ROOT');

  // Tier 1: DRAIN and CULVERT in parallel
  assert.equal(dag.tiers[1].length, 2);
  const tier1Ids = dag.tiers[1].map((n) => n.id).sort();
  assert.deepEqual(tier1Ids, ['TASK-CULVERT', 'TASK-DRAIN']);

  // Tier 2: Final Check (depends on both)
  assert.equal(dag.tiers[2].length, 1);
  assert.equal(dag.tiers[2][0].id, 'TASK-FINAL-CHECK');
});

test('computeTaskDag detects cyclic dependencies safely without hanging', () => {
  const cyclicTasks: TaskDraft[] = [
    {
      id: 'TASK-X',
      action_type: 'DRAIN_BLOCKAGE_CLEARANCE',
      target_ids: ['DRAIN-1'],
      department_id: 'DEPT-DRAIN',
      priority: 'HIGH',
      prerequisites: [],
      depends_on: ['TASK-Y'],
      evidence_ids: [],
      assessment_ids: [],
      procedure_citation: {} as any,
      expected_outcome: 'Cleared',
      verification_criteria: 'Clear',
      risks: [],
    },
    {
      id: 'TASK-Y',
      action_type: 'DRAIN_BLOCKAGE_CLEARANCE',
      target_ids: ['DRAIN-1'],
      department_id: 'DEPT-DRAIN',
      priority: 'HIGH',
      prerequisites: [],
      depends_on: ['TASK-X'],
      evidence_ids: [],
      assessment_ids: [],
      procedure_citation: {} as any,
      expected_outcome: 'Flushed',
      verification_criteria: 'Flushed',
      risks: [],
    },
  ];

  const dag = computeTaskDag(cyclicTasks);
  assert.equal(dag.hasCycle, true);
  assert.equal(dag.totalTasks, 2);
});

test('computeTaskDag merges taskBindings properties correctly', () => {
  const tasks: TaskDraft[] = [
    {
      id: 'TASK-1',
      action_type: 'DRAIN_BLOCKAGE_CLEARANCE',
      target_ids: ['DRAIN-101'],
      department_id: 'DEPT-DRAIN',
      priority: 'HIGH',
      prerequisites: ['CAUSAL_INSPECTION MET'],
      depends_on: [],
      evidence_ids: [],
      assessment_ids: [],
      procedure_citation: {} as any,
      expected_outcome: 'Restore hydraulic flow',
      verification_criteria: 'Flow clear',
      risks: ['Sediment transfer'],
    },
  ];

  const bindings: PlanTaskBinding[] = [
    {
      local_task_id: 'TASK-1',
      task_id: 'TASK-UUID-1234',
      action_type: 'DRAIN_BLOCKAGE_CLEARANCE',
      target_ids: ['DRAIN-101'],
      department_id: 'DEPT-DRAIN',
      depends_on_task_ids: [],
      status: 'PROPOSED',
      expected_hash: '1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
      eligible_assignee_ids: ['OP-DRAIN-LEAD'],
    },
  ];

  const dag = computeTaskDag(tasks, bindings);
  assert.equal(dag.nodes.length, 1);
  const node = dag.nodes[0];
  assert.equal(node.id, 'TASK-1');
  assert.equal(node.status, 'PROPOSED');
  assert.deepEqual(node.eligible_assignees, ['OP-DRAIN-LEAD']);
  assert.equal(node.expected_outcome, 'Restore hydraulic flow');
  assert.deepEqual(node.risks, ['Sediment transfer']);
});

test('formatShortHash shortens long SHA-256 and handles falsy values', () => {
  assert.equal(formatShortHash(null), 'Not recorded');
  assert.equal(formatShortHash(''), 'Not recorded');
  assert.equal(formatShortHash('short-hash'), 'short-hash');
  const sha = '1b04b300f41379529bd0e7b6667bf28c1fbaaec5f1bbe38f4cfb5803a3a74286';
  assert.equal(formatShortHash(sha), '1b04b300…a3a74286');
});

test('getStatusBadgeStyle returns semantic colors for plan and work order statuses', () => {
  const approved = getStatusBadgeStyle('APPROVED');
  assert.equal(approved.color, '#137333');

  const pending = getStatusBadgeStyle('PENDING_APPROVAL');
  assert.equal(pending.color, '#1a73e8');

  const blocked = getStatusBadgeStyle('BLOCKED');
  assert.equal(blocked.color, '#c5221f');

  const draft = getStatusBadgeStyle('DRAFT');
  assert.equal(draft.color, '#5f6368');
});

test('closed schema validation validates PlanDTO and WorkOrderDTO', () => {
  const root = resolve(import.meta.dirname, '../..');
  const schemaPath = resolve(root, 'contracts/api_models.json');
  const raw = JSON.parse(readFileSync(schemaPath, 'utf8'));

  const ajv = new Ajv({ strict: false, allErrors: true });
  for (const [key, value] of Object.entries(raw.$defs || {})) {
    ajv.addSchema(value as any, `#/$defs/${key}`);
  }

  const validatePlan = ajv.compile(raw.$defs.PlanDTO);
  const samplePlan: PlanDTO = {
    plan_id: 'PLAN-B12-da6d426cc7a42982a3dac6c8a76af2a6',
    investigation_id: 'INV-B09-8b006fb97aa2b908fc69addcf7ecd037',
    version: 1,
    content_hash: '1b04b300f41379529bd0e7b6667bf28c1fbaaec5f1bbe38f4cfb5803a3a74286',
    draft: {
      investigation_id: 'INV-B09-8b006fb97aa2b908fc69addcf7ecd037',
      issue: 'WATERLOGGING',
      version: 1,
      simulation_mode: 'SIMULATED',
      basis: [
        {
          hypothesis_id: 'HYP-B09-67069586a2c59c991ee97a506c861caf',
          assessment_id: 'ASSESS-B09-3bd930e452fc791c7121d5972a40240b',
          reason: 'Assessment found blockage',
          addressed: true,
        },
        {
          hypothesis_id: 'HYP-B09-e816856dd2ff1f7f817e573fe26215a6',
          assessment_id: 'ASSESS-B09-67fca704d96d284b17d792dbb05d7900',
          reason: 'Inconclusive capacity test',
          addressed: false,
        },
      ],
      evidence_ids: ['EV-REPORT-01'],
      tasks: [
        {
          id: 'TASK-CLEAR-DRAIN-101',
          action_type: 'DRAIN_BLOCKAGE_CLEARANCE',
          remediation: {
            mode: 'SUPPORTED_NOW',
            conditions: [
              {
                kind: 'CAUSAL_INSPECTION',
                status: 'MET',
                evidence_ids: ['EV-REPORT-01'],
              },
              {
                kind: 'SAFETY_REVIEW',
                status: 'MET',
                evidence_ids: ['EV-REPORT-01'],
              },
            ],
          },
          target_ids: ['DRAIN-101'],
          department_id: 'DEPT-DRAIN',
          priority: 'HIGH',
          prerequisites: ['CAUSAL_INSPECTION MET'],
          depends_on: [],
          evidence_ids: ['EV-REPORT-01'],
          assessment_ids: ['ASSESS-B09-3bd930e452fc791c7121d5972a40240b'],
          procedure_citation: {
            source_document_id: 'D019',
            source_version: 1,
            canonical_document_id: 'ORG:D019:1',
            owner_department_id: 'DEPT-DRAIN',
            source_uri: 'data/documents/b12r/D019_drain_blockage_clearance.md',
            content_checksum: '15bbe2e22a79c4f39a482afa711c5135eb1b8a13e660c50003c823d723dab261',
            quote_excerpt: 'Clearance procedure for drain inlet.',
            passage_location: 'chunk:0:c6a1b4b3-56b5-4941-b6ad-d302558db32f',
            chunk_sha256: 'bd681cfe32129e8fcb021237d7f5886ef12dadc94a68c3ff190ebd13703e496f',
            confidence_label: 'SOURCE_REVIEWED_SYNTHETIC',
            assertion_status: 'PROPOSED',
            retrieved_at: '2026-10-18T15:01:13.549Z',
            effective_from: '2026-10-18T00:00:00Z',
          },
          expected_outcome: 'Remove obstruction and restore conveyance in DRAIN-101.',
          verification_criteria: 'Discharge through DRAIN-101 verified clear.',
          risks: ['Downstream debris transfer during flushing operations'],
        },
      ],
      expected_outcomes: ['Restore hydraulic flow through DRAIN-101.'],
      risks: ['Downstream sediment accumulation.'],
      uncertainties: ['Residual hydraulic capacity deficit may persist.'],
      monitoring: {
        issue: 'WATERLOGGING',
        required_evidence: ['COMPARABLE_FOLLOWUP_RAINFALL', 'FOLLOWUP_WATERLOGGING'],
        observation_opportunity: 'Monitor across next significant rainfall.',
        verification_criteria: 'Absence of surface waterlogging.',
        missing_opportunity: 'UNRESOLVED',
        completion_implies_resolution: false,
      },
    },
    draft_receipt: {
      id: 'PLAN-B12-da6d426cc7a42982a3dac6c8a76af2a6',
      version: 1,
      plan_hash: '1b04b300f41379529bd0e7b6667bf28c1fbaaec5f1bbe38f4cfb5803a3a74286',
      status: 'DRAFT',
      simulation_mode: 'SIMULATED',
      approved: false,
      executable: false,
    },
    status: 'PENDING_APPROVAL',
    expected_hash: '64c961c2fa7eac6935c5dac193d73bb08b2634454a92a02c45f710b6764c5375',
    approval_status: 'PENDING_APPROVAL',
    execution_gates_verified: false,
    simulated: true,
    limitations: ['Approval does not prove execution gates are satisfied'],
  };

  assert(validatePlan(samplePlan), JSON.stringify(validatePlan.errors));

  const validateWorkOrder = ajv.compile(raw.$defs.WorkOrderDTO);
  const sampleWorkOrder: WorkOrderDTO = {
    id: 'WO-001',
    expected_hash: '64c961c2fa7eac6935c5dac193d73bb08b2634454a92a02c45f710b6764c5375',
    status: 'ASSIGNED',
    task_id: 'TASK-1',
    plan_id: 'PLAN-B12-001',
    department_id: 'DEPT-DRAIN',
    assignee_id: 'OP-DRAIN-LEAD',
    authorized_by: 'OP-APPROVER',
    status_event_ids: ['EV-STATUS-01'],
    resolution_verified: false,
  };

  assert(validateWorkOrder(sampleWorkOrder), JSON.stringify(validateWorkOrder.errors));
});
