'use client';

import { useState } from 'react';
import Link from 'next/link';
import type { ScenarioDTO } from '../lib/generated/models';
import { useDemo } from './demo-connection';
import { useRead } from './use-read';
import {
  JourneyCategory,
  filterScenariosByCategory,
  formatStageName,
  getStageBadgeClass,
  getScenarioHref,
  getScenarioIssueLabel,
  getScenarioPrimaryCase,
} from '../lib/read/journeys';
import { Icon } from './icons';

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

  if (!isOpen) return null;

  const scenarios: ScenarioDTO[] = catalog.data?.items ?? [];
  const filtered = filterScenariosByCategory(scenarios, selectedCategory);

  const categories: { key: JourneyCategory; label: string; icon: string }[] = [
    { key: 'ALL', label: 'All Scenarios (12)', icon: 'layers' },
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
              INTERACTIVE DEMO CATALOG
            </span>
            <h2 id="scenario-guide-title" style={{ margin: 0, fontSize: '1.25rem' }}>
              Municipal Scenario Journeys (S01 – S12)
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
          Explore all 12 reproducible municipal scenarios across the three civic issue categories and
          cross-category defect cascades. Select any scenario to launch its connected investigation directly.
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
          {catalog.status === 'loading' ? (
            <div className="journey-loading">
              <p>Loading scenario catalog from backend…</p>
            </div>
          ) : filtered.length === 0 ? (
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
                        {stageLabel}
                      </span>
                    </div>

                    <h3 className="scenario-title">{s.title}</h3>

                    {primaryCase && (
                      <div className="scenario-meta">
                        <div className="meta-row">
                          <span className="meta-lbl">Investigation:</span>
                          <code>{primaryCase.investigation_id}</code>
                        </div>
                        <div className="meta-row">
                          <span className="meta-lbl">Primary Asset:</span>
                          <code>{primaryCase.asset_id}</code>
                        </div>
                        <div className="meta-row">
                          <span className="meta-lbl">Assigned Dept:</span>
                          <span>{primaryCase.department_id}</span>
                        </div>
                      </div>
                    )}

                    {s.next_operator_steps && s.next_operator_steps.length > 0 && (
                      <div className="scenario-step-box">
                        <strong>Next Step:</strong> {s.next_operator_steps[0]}
                      </div>
                    )}

                    <div className="card-actions">
                      <Link
                        href={href}
                        className="button primary small-btn full-width"
                        onClick={onClose}
                      >
                        Launch Scenario Investigation <Icon name="arrow" size={14} />
                      </Link>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
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
