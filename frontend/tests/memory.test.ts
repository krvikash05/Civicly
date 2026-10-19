import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import Ajv from 'ajv';
import {
  findClusterMonitoring,
  filterRelevantProcedures,
  getMonitoringStatusStyle,
  formatQuoteExcerpt,
  explainOutcome,
  monitoringOpportunity,
} from '../lib/read/memory.ts';
import type {
  MonitoringDTO,
  ProcedureDTO,
  CaseMemoryDTO,
  OutcomeDTO,
} from '../lib/generated/models.ts';

test('follow-up descriptions distinguish utility checks, completion and episode closure',()=>{
 const out=(assessment_status:string,case_closed=false)=>({assessment_status,case_closed} as OutcomeDTO);
 assert.match(explainOutcome(out('UTILITY_VERIFIED')),/does not establish.*road problem is resolved/);
 assert.match(explainOutcome(out('MONITORING')),/separate follow-up/);
 assert.match(explainOutcome(out('RESOLUTION_VERIFIED',true)),/closed this incident episode.*future recurrence/);
 assert.match(explainOutcome(out('RESOLUTION_VERIFIED')),/did not close/);
 assert.match(explainOutcome(out('PROBLEM_PERSISTS')),/did not establish a successful resolution/);
 assert.match(explainOutcome(out('UNKNOWN')),/did not close/);
});
test('monitoring explanations describe issue-specific observation opportunities without inventing results',()=>{
 assert.match(monitoringOpportunity('WATERLOGGING'),/comparable rainfall/);
 assert.match(monitoringOpportunity('ROAD_DAMAGE'),/separate verification/);
 assert.match(monitoringOpportunity('WASTE_ACCUMULATION'),/scheduled collections with actual pickups/);
 for(const issue of ['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION'])assert.doesNotMatch(monitoringOpportunity(issue),/problem resolved|no recurrence|checks passed/i);
});

test('findClusterMonitoring finds matching cluster or returns null', () => {
  const list: MonitoringDTO[] = [
    {
      problem_cluster_id: 'PC-001',
      status: 'MONITORING',
      verification_policy: 'B14-2 policy',
      remaining_checks: ['Follow-up inspection'],
      outcome_evidence_ids: ['EV-01'],
    },
    {
      problem_cluster_id: 'PC-002',
      status: 'CONTROLLED',
      verification_policy: 'B14-2 policy',
      remaining_checks: [],
      outcome_evidence_ids: ['EV-02'],
    },
  ];

  assert.equal(findClusterMonitoring(list, 'PC-001')?.status, 'MONITORING');
  assert.equal(findClusterMonitoring(list, 'PC-002')?.status, 'CONTROLLED');
  assert.equal(findClusterMonitoring(list, 'PC-003'), null);
  assert.equal(findClusterMonitoring([], 'PC-001'), null);
  assert.equal(findClusterMonitoring(list, null), null);
});

test('filterRelevantProcedures filters by department or issue category', () => {
  const procedures: ProcedureDTO[] = [
    {
      id: 'ORG:D001:1',
      procedure_id: 'D001',
      title: 'Drain blockage inspection procedure',
      source_kind: 'SYNTHETIC',
      version: 1,
      sha256: 'b8a0f22665d1c961c0c96ad861d9576b433cea490adb82f8f86f98b21aeb4b86',
      owner_department_id: 'DEPT-DRAIN',
      citations: [],
      gaps: [],
      assertion_status: 'PROPOSED',
      trusted_as_instructions: false,
      effective_from: '2026-10-18T00:00:00Z',
    },
    {
      id: 'ORG:D002:1',
      procedure_id: 'D002',
      title: 'Road pavement and pothole repair',
      source_kind: 'SYNTHETIC',
      version: 1,
      sha256: 'c8a0f22665d1c961c0c96ad861d9576b433cea490adb82f8f86f98b21aeb4b87',
      owner_department_id: 'DEPT-ROAD',
      citations: [],
      gaps: [],
      assertion_status: 'PROPOSED',
      trusted_as_instructions: false,
      effective_from: '2026-10-18T00:00:00Z',
    },
    {
      id: 'ORG:D003:1',
      procedure_id: 'D003',
      title: 'Missed solid waste pickup recovery',
      source_kind: 'SYNTHETIC',
      version: 1,
      sha256: 'd8a0f22665d1c961c0c96ad861d9576b433cea490adb82f8f86f98b21aeb4b88',
      owner_department_id: 'DEPT-SANITATION',
      citations: [],
      gaps: [],
      assertion_status: 'PROPOSED',
      trusted_as_instructions: false,
      effective_from: '2026-10-18T00:00:00Z',
    },
  ];

  const waterProcs = filterRelevantProcedures(procedures, null, 'WATERLOGGING');
  assert.equal(waterProcs.length, 1);
  assert.equal(waterProcs[0].id, 'ORG:D001:1');

  const roadProcs = filterRelevantProcedures(procedures, null, 'ROAD_DAMAGE');
  assert.equal(roadProcs.length, 1);
  assert.equal(roadProcs[0].id, 'ORG:D002:1');

  const wasteProcs = filterRelevantProcedures(procedures, null, 'WASTE_ACCUMULATION');
  assert.equal(wasteProcs.length, 1);
  assert.equal(wasteProcs[0].id, 'ORG:D003:1');

  const allProcs = filterRelevantProcedures(procedures, null, null);
  assert.equal(allProcs.length, 3);
});

test('getMonitoringStatusStyle returns semantic status colors', () => {
  const controlled = getMonitoringStatusStyle('CONTROLLED');
  assert.equal(controlled.color, '#137333');

  const monitoring = getMonitoringStatusStyle('MONITORING');
  assert.equal(monitoring.color, '#1a73e8');

  const open = getMonitoringStatusStyle('OPEN');
  assert.equal(open.color, '#b06000');

  const reopened = getMonitoringStatusStyle('REOPENED');
  assert.equal(reopened.color, '#c5221f');
});

test('formatQuoteExcerpt handles clean truncation and whitespace normalization', () => {
  assert.equal(formatQuoteExcerpt(null), 'No excerpt recorded.');
  assert.equal(formatQuoteExcerpt(''), 'No excerpt recorded.');
  const text = 'Line 1\nLine 2\r\nLine 3';
  assert.equal(formatQuoteExcerpt(text), 'Line 1 Line 2 Line 3');
  const long = 'A'.repeat(300);
  assert.equal(formatQuoteExcerpt(long, 50).length, 51); // 50 chars + ellipsis
});

test('closed schema validation validates MonitoringDTO, ProcedureDTO, CaseMemoryDTO, and OutcomeDTO', () => {
  const root = resolve(import.meta.dirname, '../..');
  const schemaPath = resolve(root, 'contracts/api_models.json');
  const raw = JSON.parse(readFileSync(schemaPath, 'utf8'));

  const ajv = new Ajv({ strict: false, allErrors: true });
  for (const [key, value] of Object.entries(raw.$defs || {})) {
    ajv.addSchema(value as any, `#/$defs/${key}`);
  }

  // 1. MonitoringDTO
  const validateMonitoring = ajv.compile(raw.$defs.MonitoringDTO);
  const sampleMonitoring: MonitoringDTO = {
    problem_cluster_id: 'PC-B08-e05a65f1899a2b545765090629fe1a61',
    status: 'OPEN',
    verification_policy: 'B14-2; actual dated evidence/opportunity required',
    remaining_checks: ['Independent observation opportunity and verification remain required'],
    outcome_evidence_ids: [],
  };
  assert(validateMonitoring(sampleMonitoring), JSON.stringify(validateMonitoring.errors));

  // 2. ProcedureDTO
  const validateProcedure = ajv.compile(raw.$defs.ProcedureDTO);
  const sampleProcedure: ProcedureDTO = {
    id: 'ORG:D001:1',
    procedure_id: 'D001',
    title: 'Drain blockage inspection',
    source_kind: 'SYNTHETIC',
    version: 1,
    sha256: 'b8a0f22665d1c961c0c96ad861d9576b433cea490adb82f8f86f98b21aeb4b86',
    owner_department_id: 'DEPT-DRAIN',
    citations: [
      {
        source_document_id: 'D001',
        source_version: 1,
        canonical_document_id: 'ORG:D001:1',
        owner_department_id: 'DEPT-DRAIN',
        source_uri: 'data/documents/b11/D001_drain_blockage_inspection.md',
        content_checksum: 'b8a0f22665d1c961c0c96ad861d9576b433cea490adb82f8f86f98b21aeb4b86',
        quote_excerpt: 'Drain blockage inspection protocol',
        passage_location: 'chunk:0:c6a1b4b3-56b5-4941-b6ad-d302558db32f',
        chunk_sha256: 'bd681cfe32129e8fcb021237d7f5886ef12dadc94a68c3ff190ebd13703e496f',
        confidence_label: 'SOURCE_REVIEWED_SYNTHETIC',
        assertion_status: 'PROPOSED',
        retrieved_at: '2026-10-18T15:00:00Z',
        effective_from: '2026-10-18T00:00:00Z',
      },
    ],
    gaps: [],
    assertion_status: 'PROPOSED',
    trusted_as_instructions: false,
    effective_from: '2026-10-18T00:00:00Z',
  };
  assert(validateProcedure(sampleProcedure), JSON.stringify(validateProcedure.errors));

  // 3. CaseMemoryDTO
  const validateMemory = ajv.compile(raw.$defs.CaseMemoryDTO);
  const sampleMemory: CaseMemoryDTO = {
    id: 'MEM-001',
    source_investigation_id: 'INV-001',
    outcome_ids: ['OUT-001'],
    evidence_ids: ['EV-01'],
    gaps: ['Historical maintenance log missing'],
    truncated: false,
    memory_type: 'RECORDED_CASE_CONTEXT',
    summary: 'Stored historical context; absent records are evidence gaps',
  };
  assert(validateMemory(sampleMemory), JSON.stringify(validateMemory.errors));

  // 4. OutcomeDTO
  const validateOutcome = ajv.compile(raw.$defs.OutcomeDTO);
  const sampleOutcome: OutcomeDTO = {
    id: 'OUT-001',
    work_order_id: 'WO-001',
    assessment_status: 'SUPPORTED',
    result: 'DRAIN_CLEARANCE_SUCCESS',
    evidence_ids: ['EV-01'],
    evaluated_at: '2026-10-18T16:00:00Z',
    case_closed: false,
    policy_version: 'B14-2',
    simulated: true,
  };
  assert(validateOutcome(sampleOutcome), JSON.stringify(validateOutcome.errors));
});
