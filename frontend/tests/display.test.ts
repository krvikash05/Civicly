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
  translateLocation,
  translateAsset,
  translateToolAction,
  translateNextAction,
  formatMissingEvidence,
  cleanTextIdentifiers,
  explainPlanConsideration,
} from '../lib/read/display.ts';

test('plan explanation turns the recorded blockage findings into plain language', () => {
  const text = explainPlanConsideration('Assessment ASSESS-B09-3bd930e452fc791c7121d5972a40240b found BLOCKAGE supported by reviewed inspection observations FLOW_RESTRICTED and OBSTRUCTION_OBSERVED on DRAIN-101.', true);
  assert.match(text, /blocking the drain.*water from flowing freely/);
  assert.match(text, /possible cause/);
  assert.match(text, /plan includes work/);
  assert.doesNotMatch(text, /ASSESS-|FLOW_RESTRICTED|OBSTRUCTION_OBSERVED|DRAIN-101|verified|proven/i);
});

test('plan explanation keeps insufficient evidence and excluded work distinct', () => {
  const text = explainPlanConsideration('Alternative hypothesis CAPACITY_DEFICIT assessed as INCONCLUSIVE due to lack of discriminating capacity test evidence.', false);
  assert.match(text, /not enough evidence/);
  assert.match(text, /does not include work/);
  assert.doesNotMatch(text, /ruled out|no capacity problem|CAPACITY_DEFICIT/);
});

test('plan explanation preserves structural support and evidence against a pipe leak', () => {
  assert.match(explainPlanConsideration('Assessment evaluated confirming physical observations STRUCTURAL_TEST_FAILED and SUBGRADE_FAILURE_OBSERVED on ROAD-DEMO-SUBGRADE-02, supporting subgrade failure mechanism.', true), /ground beneath the road/);
  const text = explainPlanConsideration('Assessment evaluated normal pressure test observation PRESSURE_TEST_NORMAL on PIPE-DEMO-NORMAL-02, contradicting the competing utility leak hypothesis.', false);
  assert.match(text, /pressure test was normal.*argues against a pipe leak/);
  assert.doesNotMatch(text, /no leak exists|PRESSURE_TEST_NORMAL/);
});

test('plan explanation retains conditional work and uncertain damage extent', () => {
  assert.match(explainPlanConsideration('Reviewed bounded mechanism supports conditional simulated remedy', true), /provided the conditions.*simulated/);
  assert.match(explainPlanConsideration('Retained uncertain extent does not authorize additional work', false), /still uncertain.*does not justify extra work/);
});

test('unknown coded plan notes remain neutral and point to their preserved original', () => {
  const text = explainPlanConsideration('Assessment ASSESS-B09-unknown found NEW_TEST_CODE.', false);
  assert.match(text, /original assessment note/);
  assert.doesNotMatch(text, /NEW_TEST_CODE|supports|verified/);
  assert.match(explainPlanConsideration('A further inspection is needed.', false), /^A further inspection is needed\./);
});

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
  assert.equal(fallback.title, 'Unusual Vibration');
  assert.equal(fallback.explanation, 'Hypothesis recorded during diagnostic reasoning.');

  const wasteShortfall = translateCauseCode('CAPACITY_SHORTFALL');
  assert.equal(wasteShortfall.title, 'Solid Waste Container Capacity Shortfall');

  const missedPickup = translateCauseCode('MISSED_PICKUP');
  assert.equal(missedPickup.title, 'Missed Municipal Collection Cycle');
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
  assert.equal(translateDepartment('DEPT-WATER'), 'Water Utilities');
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

test('formatShortIdentifier shortens technical IDs without losing identity and trims long hashes', () => {
  assert.equal(formatShortIdentifier('PLAN-B12-REPAIR-42'), 'REPAIR-42');
  assert.equal(formatShortIdentifier('INV-2026-OCT-18-01'), 'OCT-18-01');
  assert.equal(formatShortIdentifier('SHORT'), 'SHORT');
  assert.equal(formatShortIdentifier('INV-B09-a2fe3dbdecd03984033026c4d0856295'), 'B09-a2fe3d');
  assert.equal(formatShortIdentifier('INC-B08-1cca34465b82269a84275ff0d1a4732d'), 'B08-1cca34');
});

test('formatIssueName formats issue categories', () => {
  assert.equal(formatIssueName('WATERLOGGING'), 'Waterlogging');
  assert.equal(formatIssueName('ROAD_DAMAGE'), 'Road damage');
  assert.equal(formatIssueName('WASTE_ACCUMULATION'), 'Waste accumulation');
});

test('translateLocation translates raw location codes into human sites', () => {
  assert.equal(translateLocation('LOC-JUNCTION'), 'Market Junction');
  assert.equal(translateLocation('LOC-MARKET'), 'Central Market');
  assert.equal(translateLocation('LOC-WASTE-DEMO-DUMPING'), 'Commercial Waste Disposal Zone');
  assert.equal(translateLocation('LOC-WASTE-DEMO-SERVICE-02'), 'Commercial Sanitation Sector 02');
  assert.equal(translateLocation('LOC-005'), 'Civic District Site 05');
});

test('translateAsset translates asset codes into human descriptive names', () => {
  assert.equal(translateAsset('WASTE-DEMO-SERVICE-02'), 'Commercial Waste Collection Point #02');
  assert.equal(translateAsset('WASTE-100'), 'Central Market Waste Collection Point');
  assert.equal(translateAsset('DRAIN-100'), 'Stormwater Inlet Grate #100');
  assert.equal(translateAsset('ROAD-100'), 'Market Approach Roadway Segment #100');
  assert.equal(translateAsset('PIPE-100'), 'Pressurized Water Supply Main #100');
});

test('translateToolAction translates MCP tool names into readable action descriptions', () => {
  assert.equal(translateToolAction('civicly::get_pickup_execution_history'), 'Query sanitation pickup execution history');
  assert.equal(translateToolAction('official::query_graph_readonly'), 'Execute readonly FalkorDB graph traversal');
  assert.equal(translateToolAction('civicly::retrieve_external_evidence'), 'Retrieve meteorological & sensor observations');
});

test('translateNextAction translates workflow next actions', () => {
  assert.equal(translateNextAction('DURABLE_WORKER_OR_HUMAN_REVIEW'), 'Review the saved case and its next required step');
  assert.equal(translateNextAction('AWAITING_APPROVAL'), 'Supervisory approval pending');
});

test('formatMissingEvidence transforms raw machine evidence tokens into clear checklists', () => {
  assert.equal(
    formatMissingEvidence('BIN_CAPACITY_EXCEEDED,EXPECTED_PICKUPS_COMPLETED'),
    'Audit of container capacity vs. peak disposal volume; Verification of municipal sanitation collection logs'
  );
  assert.equal(
    formatMissingEvidence('EV-B08-2825858884520ab1d5bcfd47921c2402'),
    'Evidence reference #B08-282585 needs review'
  );
});

test('cleanTextIdentifiers sanitizes raw machine tokens in sentences', () => {
  assert.equal(
    cleanTextIdentifiers('What does the physical graph record show for asset WASTE-DEMO-SERVICE-02?'),
    'What does the physical graph record show for asset Commercial Waste Collection Point #02?'
  );
  assert.equal(
    cleanTextIdentifiers('Execute civicly::get_pickup_execution_history at LOC-MARKET'),
    'Execute Query sanitation pickup execution history at Central Market'
  );
});
