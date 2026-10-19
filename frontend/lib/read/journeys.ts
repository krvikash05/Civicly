/**
 * Scenario Journey Helpers for Civicly F08
 */

import type { ScenarioDTO, ScenarioCase } from '../generated/models';
import type {DirectoryCase} from './workflow.ts';

export const SUGGESTED_JOURNEY_ID='INV-B09-b9d4d66e130ed348c4f6a50e9d66a891';

/** Curate only returned investigations; a catalog definition is not a solved case. */
export function groupJourneys(rows:DirectoryCase[],category:JourneyCategory){
  const unique=rows.filter((r,i)=>rows.findIndex(other=>other.investigation_id===r.investigation_id&&other.issue_type===r.issue_type)===i);
  const available=unique.filter(c=>category==='ALL'||(category==='CROSS_CATEGORY'
    ?unique.some(other=>other.investigation_id===c.investigation_id&&other.issue_type!==c.issue_type)
    :c.issue_type===category));
  return {
    completed:available.filter(c=>c.stage==='COMPLETED').sort((a,b)=>Number(b.investigation_id===SUGGESTED_JOURNEY_ID)-Number(a.investigation_id===SUGGESTED_JOURNEY_ID)),
    ongoing:available.filter(c=>c.stage!=='COMPLETED'&&c.stage!=='CANCELLED').sort((a,b)=>Number(b.stage==='MONITORING')-Number(a.stage==='MONITORING')),
    cancelled:available.filter(c=>c.stage==='CANCELLED'),
  };
}

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

export function getScenarioHref(scenario: ScenarioDTO): string | null {
  const primaryCase = getScenarioPrimaryCase(scenario);
  if (!primaryCase) return null;
  if (primaryCase.investigation_id) {
    return `/investigations?investigation=${encodeURIComponent(primaryCase.investigation_id)}&section=report`;
  }
  if (primaryCase.incident_id) {
    return `/investigations?incident=${encodeURIComponent(primaryCase.incident_id)}&section=report`;
  }
  return null;
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
