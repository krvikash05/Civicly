'use client';
import { useState, Suspense } from 'react';
import Link from 'next/link';
import { Icon } from '../components/icons';
import { ConnectionNotice, useDemo } from '../components/demo-connection';
import { useRead } from '../components/use-read';
import { ReadMessage } from '../components/read-state';
import { metrics, displayTime } from '../lib/read/cases';
import { CaseDirectory } from '../components/case-directory';
import { useEventStream } from '../components/use-event-stream';
import { LiveStreamPanel } from '../components/live-stream-panel';
import { ScenarioJourneyGuide } from '../components/scenario-journey-guide';

export default function Overview() {
  const demo = useDemo();
  const [isJourneysOpen, setIsJourneysOpen] = useState(false);
  const summary = useRead('dashboard-summary', async signal => (
    await demo.connection.client.request('GET /api/v1/dashboard/summary', { signal })
  ).data);

  const stream = useEventStream({
    token: demo.status === 'connected' ? demo.connection.getToken() : null,
    onRefetch: () => {
      summary.refresh();
    },
  });


  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">THE BIG PICTURE</p>
          <h1>A clearer view of your city.</h1>
          <p>Understand recurring problems. Follow the evidence. Coordinate what comes next.</p>
        </div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <button
            type="button"
            className="button secondary"
            onClick={() => setIsJourneysOpen(true)}
            aria-haspopup="dialog"
          >
            <Icon name="layers" size={17} /> Scenario Journeys (S01–S12)
          </button>
          <Link className="button primary" href="/investigations">
            Open investigations <Icon name="arrow" size={17} />
          </Link>
        </div>
      </div>

      <ConnectionNotice />

      <section aria-label="Case overview" className="metrics">
        {metrics.map(({ field, label, icon, description }) => {
          const value = summary.status === 'ready' && summary.data ? summary.data[field] : null;
          const displayVal = summary.status === 'loading' ? '…' : value !== null && value !== undefined ? String(value) : '—';
          return (
            <article className="metric" key={label}>
              <div className="metric-top">
                <span>{label}</span>
                <Icon name={icon} />
              </div>
              <div className="metric-value" aria-label={value !== null ? `${label}: ${displayVal}` : 'Unavailable'}>
                {displayVal}
              </div>
              <p>{description}</p>
            </article>
          );
        })}
      </section>

      {summary.status === 'error' && (
        <div style={{ marginBottom: 20 }}>
          <ReadMessage state={summary} retry={summary.refresh} />
        </div>
      )}

      {summary.data && (
        <div className="meta-bar">
          <div className="meta-info">
            <span>Recorded as of: <strong>{displayTime(summary.data.as_of)}</strong></span>
            <span className="meta-sep">·</span>
            <span>Graph revision: <strong>{summary.data.graph_revision}</strong></span>
            {summary.data.simulation_mode && <span className="small-tag">SIMULATED</span>}
          </div>
          {(summary.data.definitions?.length || summary.data.limitations?.length) ? (
            <details className="resource-notes">
              <summary>Metric definitions &amp; data limitations</summary>
              {summary.data.definitions?.map((def, idx) => (
                <p key={'def-' + idx}><strong>Definition:</strong> {def}</p>
              ))}
              {summary.data.limitations?.map((lim, idx) => (
                <p key={'lim-' + idx}><strong>Limitation:</strong> {lim}</p>
              ))}
            </details>
          ) : null}
        </div>
      )}

      <div className="overview-grid">
        <section className="panel issues-panel">
          <div className="panel-heading">
            <div>
              <h2>Recurring problems</h2>
              <p>Three issue categories. One connected investigation.</p>
            </div>
            <span className="small-label">DEMO CITY</span>
          </div>

          <div className="issue-categories">
            {[
              ['water', 'Waterlogging', 'Drainage & accumulation', 'WATERLOGGING'],
              ['road', 'Road damage', 'Pavement & recurring repairs', 'ROAD_DAMAGE'],
              ['waste', 'Waste accumulation', 'Collection & service patterns', 'WASTE_ACCUMULATION'],
            ].map(([icon, label, description, issueKey]) => {
              const activeCount = summary.data?.issue_counts?.[issueKey];
              const recurCount = summary.data?.recurrence_counts?.[issueKey];
              return (
                <Link className={`issue-category ${icon}`} key={icon} href={`/investigations?issue=${issueKey}`}>
                  <span className="issue-icon"><Icon name={icon} /></span>
                  <strong>{label}</strong>
                  <small>{description}</small>
                  <div className="issue-metrics">
                    <span>{activeCount !== undefined ? `${activeCount} active` : '—'}</span>
                    <span className="metric-dot">·</span>
                    <span>{recurCount !== undefined ? `${recurCount} recurrent` : '—'}</span>
                  </div>
                  <span className="category-link">View investigations <span aria-hidden="true">↗</span></span>
                </Link>
              );
            })}
          </div>

          <div style={{ padding: '0 22px 22px' }}>
            <Suspense fallback={<p className="directory-empty">Loading directory…</p>}>
              <CaseDirectory />
            </Suspense>
          </div>
        </section>

        <section className="panel activity-panel">
          <div className="panel-heading">
            <div>
              <h2>Latest activity</h2>
              <p>The record of what actually happened.</p>
            </div>
            <Icon name="clock" />
          </div>
          <div className="activity-content">
            <LiveStreamPanel
              status={stream.status}
              lastEventId={stream.lastEventId}
              events={stream.events}
              onReconnect={stream.reconnect}
              onClear={stream.clearEvents}
              title="Real-Time Event Stream"
              defaultExpanded={true}
            />
            {summary.data && (
              <div className="activity-details">
                <div className="activity-row">
                  <span>Current graph revision</span>
                  <strong>{summary.data.graph_revision}</strong>
                </div>
                <div className="activity-row">
                  <span>Open problem clusters</span>
                  <strong>{summary.data.open_clusters}</strong>
                </div>
                <div className="activity-row">
                  <span>Active investigations</span>
                  <strong>{summary.data.active_investigations}</strong>
                </div>
                <div className="activity-row">
                  <span>Pending plan approvals</span>
                  <strong>{summary.data.pending_approvals}</strong>
                </div>
              </div>
            )}
          </div>
        </section>
      </div>

      <section className="graph-intro">
        <div className="intro-icon"><Icon name="graph" size={34} /></div>
        <div>
          <p className="eyebrow">EVIDENCE, CONNECTED</p>
          <h2>See why the agent takes its next step.</h2>
          <p>Follow the question, the graph paths retrieved from FalkorDB, and the recorded decision—all inside the investigation.</p>
        </div>
        <Link className="button secondary" href="/investigations#graph-evidence">
          Explore the workspace <Icon name="arrow" size={17} />
        </Link>
      </section>

      <ScenarioJourneyGuide
        isOpen={isJourneysOpen}
        onClose={() => setIsJourneysOpen(false)}
      />
    </>
  );
}
