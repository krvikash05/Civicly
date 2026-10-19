'use client';

import { useState } from 'react';
import Link from 'next/link';
import type { ScenarioDTO } from '../lib/generated/models';
import { useDemo } from './demo-connection';
import { useRead } from './use-read';
import {
  JourneyCategory,
  groupJourneys,
  SUGGESTED_JOURNEY_ID,
  filterScenariosByCategory,
  formatStageName,
  getStageBadgeClass,
  getScenarioHref,
  getScenarioIssueLabel,
  getScenarioPrimaryCase,
} from '../lib/read/journeys';
import { Icon } from './icons';
import { ReadMessage } from './read-state';
import { registeredCases, caseHref, issueName } from '../lib/read/cases';
import { loadDirectory } from '../lib/read/workflow';
import { formatShortIdentifier, translateStatus, translateAsset, translateDepartment } from '../lib/read/display';

interface ScenarioJourneyGuideProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ScenarioJourneyGuide({ isOpen, onClose }: ScenarioJourneyGuideProps) {
  const demo = useDemo();
  const [selectedCategory, setSelectedCategory] = useState<JourneyCategory>('ALL');

  const catalog = useRead(
    'journey-scenarios-catalog',
    async (signal) =>
      (await demo.connection.client.request('GET /api/v1/demo/scenarios', { signal })).data,
    isOpen
  );
  const investigations = useRead(
    `journey-investigations:${catalog.status}`,
    signal => loadDirectory(demo.connection.client, catalog.data ? registeredCases(catalog.data) : [], undefined, signal),
    isOpen && catalog.status !== 'loading'
  );

  if (!isOpen) return null;

  const scenarios: ScenarioDTO[] = catalog.data?.items ?? [];
  const filtered = filterScenariosByCategory(scenarios, selectedCategory);
  const groups=groupJourneys(investigations.data?.items??[],selectedCategory);
  const journeyGroups=[
    {id:'completed',title:'Completed investigations',description:'Start here to follow a saved investigation through its findings and response. Review Monitoring & memory for the verified outcome.',items:groups.completed},
    {id:'ongoing',title:'Still in progress',description:'These cases may need evidence, review, work or follow-up. Open one to see its current next step.',items:groups.ongoing},
    {id:'cancelled',title:'Cancelled investigations',description:'Retained case history; no continuation is implied.',items:groups.cancelled},
  ];

  const categories: { key: JourneyCategory; label: string; icon: string }[] = [
    { key: 'ALL', label: 'All issues', icon: 'layers' },
    { key: 'WATERLOGGING', label: 'Waterlogging', icon: 'water' },
    { key: 'ROAD_DAMAGE', label: 'Road Damage', icon: 'road' },
    { key: 'WASTE_ACCUMULATION', label: 'Waste Accumulation', icon: 'waste' },
    { key: 'CROSS_CATEGORY', label: 'Cross-Category', icon: 'graph' },
  ];

  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="scenario-guide-title"
    >
      <div className="modal-card journey-modal-card">
        <div className="modal-header">
          <div>
            <span className="badge badge-candidate" style={{ marginBottom: 6, display: 'inline-block' }}>
              EXPLORE CIVICLY
            </span>
            <h2 id="scenario-guide-title" style={{ margin: 0, fontSize: '1.25rem' }}>
              Choose a journey
            </h2>
          </div>
          <button
            type="button"
            className="modal-close"
            onClick={onClose}
            aria-label="Close scenario journeys dialog"
          >
            ✕
          </button>
        </div>

        <p className="journey-lead">
          Explore the reported problem, the evidence behind the response and what happened afterwards.
          Opening a journey reads its saved records; field work and observations are simulated.
        </p>

        {/* Category Filters */}
        <div className="journey-filter-bar" role="tablist" aria-label="Scenario issue filter">
          {categories.map(({ key, label, icon }) => (
            <button
              key={key}
              type="button"
              role="tab"
              aria-selected={selectedCategory === key}
              className={`journey-filter-btn ${selectedCategory === key ? 'active' : ''}`}
              onClick={() => setSelectedCategory(key)}
            >
              <Icon name={icon} size={15} />
              <span>{label}</span>
            </button>
          ))}
        </div>

        {/* Scenarios Grid */}
        <div className="journey-scenarios-scroll">
          {investigations.status !== 'ready' ? <ReadMessage state={catalog.status==='loading'?catalog:investigations} resourceName="available investigations" retry={investigations.refresh} /> : (
            <>
              {journeyGroups.filter(group=>group.items.length>0).map(group=><section className="journey-group" key={group.id} aria-label={group.title}>
                <div className="journey-group-heading"><h3>{group.title}</h3><span>{group.items.length}</span></div>
                <p className="journey-group-description">{group.description}</p>
                <div className="journey-grid">
                  {group.items.map(c=>{
                    const suggested=c.stage==='COMPLETED'&&c.investigation_id===SUGGESTED_JOURNEY_ID;
                    return <article className={`journey-card curated-journey-card${suggested?' suggested-journey':''}`} key={`${c.investigation_id}:${c.issue_type}`}>
                      <div className="curated-journey-top"><span>{issueName(c.issue_type)}</span><span className={c.stage==='COMPLETED'?'badge badge-verified':'badge badge-candidate'}>{suggested?'Suggested first journey':c.stage==='COMPLETED'?'Investigation complete':translateStatus(c.stage)}</span></div>
                      <h4>{c.glimpse??'Report details not available'}</h4>
                      <p className="curated-journey-location">{c.location??'Location not recorded'}</p>
                      <p className="curated-journey-focus">{suggested?'Follow the road and water-utility investigation, coordinated work and recorded follow-up.':c.stage==='MONITORING'?'Review the response and the observations still needed to assess its outcome.':c.stage==='COMPLETED'?'Follow the evidence, recorded response and episode history.':'Review what has been found and what still needs attention.'}</p>
                      <div className="curated-journey-footer"><small>Case #{formatShortIdentifier(c.investigation_id)}</small><Link href={caseHref({incident:c.incident_id,investigation:c.investigation_id,section:'report'})} className="button secondary small-btn full-width" onClick={onClose}>Start with the report <Icon name="arrow" size={14}/></Link></div>
                    </article>;
                  })}
                </div>
              </section>)}
              {!journeyGroups.some(group=>group.items.length>0)&&<p className="journey-empty">No connected investigation was returned for this category. Browse the prepared scenarios below.</p>}
            </>
          )}
          {investigations.data?.next_cursor && <p className="muted text-sm">This is a bounded list. More investigations may be available in the case directory.</p>}
          <details className="journey-catalog"><summary>Browse the full scenario catalog (S01–S12)</summary>
          <h3>Prepared scenarios</h3>
          <p className="muted text-sm">These definitions are separate from the available investigations above. A scenario without a connected run needs presenter setup; it is not a completed journey.</p>
          {catalog.status !== 'ready' ? <ReadMessage state={catalog} resourceName="scenario catalog" retry={catalog.refresh} /> : filtered.length === 0 ? (
            <div className="journey-empty">
              <p>No scenarios found for this category.</p>
            </div>
          ) : (
            <div className="journey-grid">
              {filtered.map((s) => {
                const primaryCase = getScenarioPrimaryCase(s);
                const issueLabel = getScenarioIssueLabel(s);
                const stageLabel = formatStageName(s.current_stage ?? s.stage);
                const href = getScenarioHref(s);

                return (
                  <article key={s.id} className="journey-card">
                    <div className="card-top">
                      <div className="card-id-block">
                        <span className="scenario-id-tag">{s.id}</span>
                        <span className="scenario-issue-pill">{issueLabel}</span>
                      </div>
                      <span className={getStageBadgeClass(s.current_stage ?? s.stage)}>
                        {href ? stageLabel : 'No connected run'}
                      </span>
                    </div>

                    <h3 className="scenario-title">{s.title}</h3>

                    {primaryCase && (
                      <div className="scenario-meta">
                        <div className="meta-row">
                          <span className="meta-lbl">Investigation:</span>
                          <span>#{formatShortIdentifier(primaryCase.investigation_id)}</span>
                        </div>
                        <div className="meta-row">
                          <span className="meta-lbl">Primary Asset:</span>
                          <span>{translateAsset(primaryCase.asset_id)}</span>
                        </div>
                        <div className="meta-row">
                          <span className="meta-lbl">Assigned Dept:</span>
                          <span>{translateDepartment(primaryCase.department_id)}</span>
                        </div>
                      </div>
                    )}

                    {!href && (
                      <div className="scenario-step-box">
                        <strong>Presenter setup needed.</strong> No investigation is connected to this scenario in the current demo.
                      </div>
                    )}

                    <div className="card-actions">
                      {href ? <Link
                        href={href}
                        className="button primary small-btn full-width"
                        onClick={onClose}
                      >
                        Open connected investigation <Icon name="arrow" size={14} />
                      </Link> : <button type="button" className="button secondary small-btn full-width" disabled>No connected investigation</button>}
                      {(s.cases ?? []).slice(1).map(c => <Link key={c.investigation_id} href={caseHref({incident:c.incident_id,investigation:c.investigation_id,section:'report'})} className="button secondary small-btn full-width" onClick={onClose}>Open {issueName(c.issue_type)} investigation</Link>)}
                    </div>
                  </article>
                );
              })}
            </div>
          )}
          </details>
        </div>

        <div className="modal-footer" style={{ marginTop: 20 }}>
          <button type="button" className="button secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
