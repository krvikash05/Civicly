import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  translateStatus,
  translateCauseCode,
  translateAssessment,
  translateActionType,
  translateDepartment,
  translateRole,
  formatEntityDisplayName,
  formatShortIdentifier,
  formatIssueName,
} from '../lib/read/display.ts';

test('translateStatus provides human-readable labels for municipal and plan states', () => {
  assert.equal(translateStatus('PENDING_APPROVAL'), 'Awaiting approval');
  assert.equal(translateStatus('APPROVED'), 'Approved');
  assert.equal(translateStatus('REJECTED'), 'Rejected');
  assert.equal(translateStatus('IN_PROGRESS'), 'In progress');
  assert.equal(translateStatus('STRUCTURAL_TEST_FAILED'), 'Structural test failed');
  assert.equal(translateStatus('SUBGRADE_FAILURE_OBSERVED'), 'Failure observed in the ground beneath the road');
  assert.equal(translateStatus('PRESSURE_TEST_NORMAL'), 'Pressure test was normal');
  assert.equal(translateStatus('FLOW_RESTRICTED'), 'Flow restricted');
  assert.equal(translateStatus('NOT_STARTED'), 'Not started');
  assert.equal(translateStatus(null), 'Not recorded');
  assert.equal(translateStatus(undefined), 'Not recorded');
  // Unknown statuses fallback neutrally without inventing facts
  assert.equal(translateStatus('CUSTOM_UNKNOWN_STATE'), 'Custom Unknown State');
});

test('translateCauseCode provides clear titles and contextual explanations', () => {
  const subgrade = translateCauseCode('HYP-SUBGRADE');
  assert.equal(subgrade.title, 'Subgrade Failure');
  assert.match(subgrade.explanation, /ground.*supporting.*road/);

  const drain = translateCauseCode('HYP-DRAIN-CLOG');
  assert.equal(drain.title, 'Drainage Inflow Blockage');
  assert.match(drain.explanation, /sediment/);

  const leak = translateCauseCode('HYP-WATER-MAIN-LEAK');
  assert.equal(leak.title, 'Pressurized Water Main Leak');

  // Fallback for custom or unknown codes
  const fallback = translateCauseCode('HYP-UNUSUAL-VIBRATION');
  assert.equal(fallback.title, 'Possible cause: HYP-UNUSUAL-VIBRATION');
  assert.equal(fallback.explanation, 'Hypothesis recorded during diagnostic reasoning.');
});

test('translateAssessment separates evidence assessment from plan coverage', () => {
  const supported = translateAssessment('SUPPORTED');
  assert.equal(supported.label, 'Supported');
  assert.equal(supported.isSupported, true);
  assert.equal(supported.isContradicted, false);
  assert.equal(supported.badgeClass, 'badge-verified');

  const contradicted = translateAssessment('CONTRADICTED');
  assert.equal(contradicted.label, 'Contradicted');
  assert.equal(contradicted.isContradicted, true);
  assert.equal(contradicted.isSupported, false);
  assert.equal(contradicted.badgeClass, 'badge-danger');

  const inconclusive = translateAssessment('INCONCLUSIVE');
  assert.equal(inconclusive.label, 'Inconclusive');
  assert.equal(inconclusive.isInconclusive, true);
  assert.equal(inconclusive.badgeClass, 'badge-warning');

  const unassessed = translateAssessment('UNASSESSED');
  assert.equal(unassessed.label, 'Awaiting evaluation');
});

test('translateActionType maps municipal action codes to readable titles', () => {
  assert.equal(translateActionType('EXCAVATE_TRENCH'), 'Trench excavation');
  assert.equal(translateActionType('CLEAR_CULVERT'), 'Culvert clearance');
  assert.equal(translateActionType('PATCH_ASPHALT'), 'Asphalt pavement patching');
  assert.equal(translateActionType('INSPECT_MANHOLE'), 'Manhole inspection');
  assert.equal(translateActionType('CUSTOM_ACTION'), 'Custom Action');
});

test('translateDepartment maps department codes to official municipal units', () => {
  assert.equal(translateDepartment('DEPT-ROADS'), 'Roads & Infrastructure Maintenance');
  assert.equal(translateDepartment('DEPT-WATER'), 'Water & Sewage Utility');
  assert.equal(translateDepartment('DEPT-ENVIRONMENT'), 'Environmental & Waste Management');
  assert.equal(translateDepartment('DEPT-PUBLIC-WORKS'), 'Public Works Department');
  assert.equal(translateDepartment('DEPT-NEW'), 'DEPT-NEW');
});

test('translateRole translates security operator roles', () => {
  assert.equal(translateRole('OPERATOR_ANALYST'), 'Investigation Analyst');
  assert.equal(translateRole('OPERATOR_APPROVER'), 'Supervising Approval Officer');
  assert.equal(translateRole('OPERATOR_FIELD_LEAD'), 'Field Operations Lead');
  assert.equal(translateRole('OPERATOR_AUDITOR'), 'Compliance Auditor');
});

test('formatEntityDisplayName formats human-readable primary labels with short IDs', () => {
  const road = formatEntityDisplayName({
    id: 'ASSET-ROAD-SEG-402',
    name: 'North Ring Road Segment 4',
    kind: 'InfrastructureAsset',
  });
  assert.equal(road.primary, 'North Ring Road Segment 4');
  assert.equal(road.shortId, 'SEG-402');

  const hyp = formatEntityDisplayName({
    id: 'HYP-B09-SUBGRADE-01',
    statement: 'Ground subgrade subsidence caused road fracture',
    kind: 'Hypothesis',
  });
  assert.equal(hyp.primary, 'Subgrade Failure');
  assert.equal(hyp.shortId, 'SUBGRADE-01');

  const fallback = formatEntityDisplayName({
    id: 'UNKNOWN-ID-XYZ',
  });
  assert.equal(fallback.primary, 'Civic entity');
  assert.equal(fallback.shortId, 'ID-XYZ');
});

test('formatShortIdentifier shortens technical IDs without losing identity', () => {
  assert.equal(formatShortIdentifier('PLAN-B12-REPAIR-42'), 'REPAIR-42');
  assert.equal(formatShortIdentifier('INV-2026-OCT-18-01'), 'OCT-18-01');
  assert.equal(formatShortIdentifier('SHORT'), 'SHORT');
});

test('formatIssueName formats issue categories', () => {
  assert.equal(formatIssueName('WATERLOGGING'), 'Waterlogging');
  assert.equal(formatIssueName('ROAD_DAMAGE'), 'Road damage');
  assert.equal(formatIssueName('WASTE_ACCUMULATION'), 'Waste accumulation');
});
