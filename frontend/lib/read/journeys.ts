/**
 * Scenario Journey Helpers for Civicly F08
 */

import type { ScenarioDTO, ScenarioCase } from '../generated/models';

export type JourneyCategory = 'ALL' | 'WATERLOGGING' | 'ROAD_DAMAGE' | 'WASTE_ACCUMULATION' | 'CROSS_CATEGORY';

export function filterScenariosByCategory(
  scenarios: ScenarioDTO[],
  category: JourneyCategory
): ScenarioDTO[] {
  if (category === 'ALL') return scenarios;
  if (category === 'CROSS_CATEGORY') {
    return scenarios.filter((s) => s.issue_types && s.issue_types.length > 1);
  }
  return scenarios.filter((s) => s.issue_types && s.issue_types.includes(category));
}

export function formatStageName(stage: string | null | undefined): string {
  switch (stage) {
    case 'BASELINE_VISIBLE':
      return '1. Baseline Reports';
    case 'EVIDENCE_REVEALED':
      return '2. Evidence & Hypotheses';
    case 'PLAN_AND_APPROVAL':
      return '3. Plan & Approval';
    case 'FOLLOW_UP':
      return '4. Post-Work Monitoring';
    case 'NOT_STARTED':
      return 'Pending Activation';
    default:
      return stage || 'Active';
  }
}

export function getStageBadgeClass(stage: string | null | undefined): string {
  switch (stage) {
    case 'FOLLOW_UP':
      return 'badge badge-verified';
    case 'PLAN_AND_APPROVAL':
      return 'badge badge-warning';
    case 'EVIDENCE_REVEALED':
      return 'badge badge-active';
    case 'BASELINE_VISIBLE':
      return 'badge badge-candidate';
    default:
      return 'badge';
  }
}

export function getScenarioPrimaryCase(scenario: ScenarioDTO): ScenarioCase | null {
  if (!scenario.cases || scenario.cases.length === 0) return null;
  return scenario.cases[0];
}

export function getScenarioHref(scenario: ScenarioDTO): string {
  const primaryCase = getScenarioPrimaryCase(scenario);
  if (!primaryCase) return '/investigations';
  if (primaryCase.investigation_id) {
    return `/investigations?investigation=${encodeURIComponent(primaryCase.investigation_id)}`;
  }
  if (primaryCase.incident_id) {
    return `/investigations?incident=${encodeURIComponent(primaryCase.incident_id)}`;
  }
  return '/investigations';
}

export function getScenarioIssueLabel(scenario: ScenarioDTO): string {
  if (!scenario.issue_types || scenario.issue_types.length === 0) return 'General';
  if (scenario.issue_types.length > 1) return 'Cross-Category';
  switch (scenario.issue_types[0]) {
    case 'WATERLOGGING':
      return 'Waterlogging';
    case 'ROAD_DAMAGE':
      return 'Road Damage';
    case 'WASTE_ACCUMULATION':
      return 'Waste Accumulation';
    default:
      return scenario.issue_types[0];
  }
}
