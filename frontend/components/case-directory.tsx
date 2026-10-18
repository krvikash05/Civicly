'use client';

import Link from 'next/link';
import { useSearchParams, useRouter } from 'next/navigation';
import { useDemo } from './demo-connection';
import { useRead } from './use-read';
import { ReadMessage } from './read-state';
import {
  registeredCases,
  uniqueCaseForIncident,
  caseHref,
  issueName,
  displayTime,
  type Issue,
  type RegisteredCase,
} from '../lib/read/cases';
import {
  translateStatus,
  formatShortIdentifier,
} from '../lib/read/display';
import { Icon } from './icons';

export function CaseDirectory({
  issue,
  invalidFilter = false,
}: {
  issue?: Issue;
  invalidFilter?: boolean;
}) {
  const demo = useDemo();
  const search = useSearchParams();
  const router = useRouter();
  const cursor = search.get('cursor') ?? undefined;

  const catalog = useRead(
    'registered-cases',
    async (signal) =>
      (await demo.connection.client.request('GET /api/v1/demo/scenarios', { signal })).data,
    !invalidFilter
  );

  const invList = useRead(
    `live-investigations:${issue ?? ''}`,
    async (signal) => {
      try {
        return (
          await demo.connection.client.request('GET /api/v1/investigations', {
            query: { limit: 20 },
            signal,
          })
        ).data;
      } catch {
        return null;
      }
    },
    !invalidFilter
  );

  const page = useRead(
    `incidents:${issue ?? ''}:${cursor ?? ''}`,
    async (signal) =>
      (
        await demo.connection.client.request('GET /api/v1/incidents', {
          query: { issue, limit: 10, cursor },
          signal,
        })
      ).data,
    !invalidFilter
  );

  type DirectoryCase = {
    investigation_id: string;
    incident_id: string;
    issue_type: Issue | string;
    stage: string;
    title?: string;
  };

  const scenarioCases: RegisteredCase[] = catalog.data ? registeredCases(catalog.data, issue) : [];
  const liveCases: DirectoryCase[] = (invList.data?.items ?? [])
    .filter((inv) => !scenarioCases.some((sc) => sc.investigation_id === inv.id))
    .map((inv) => ({
      investigation_id: inv.id,
      incident_id: inv.incident_ids[0] ?? '',
      issue_type: issue ?? 'WATERLOGGING',
      stage: inv.status,
      title: `${issueName(issue || 'WATERLOGGING')} Investigation`,
    }));
  const cases: DirectoryCase[] = [...scenarioCases, ...liveCases];

  function pageTo(newCursor?: string) {
    if (typeof window === 'undefined') return;
    const url = new URL(window.location.href);
    if (newCursor) url.searchParams.set('cursor', newCursor);
    else url.searchParams.delete('cursor');
    url.hash = 'case-directory';
    router.push(url.pathname + url.search + url.hash, { scroll: false });
  }

  function getLinkedInvId(incidentId: string): string | undefined {
    const fromCases = scenarioCases.length ? uniqueCaseForIncident(scenarioCases, incidentId) : undefined;
    if (fromCases) return fromCases.investigation_id;
    const fromInv = invList.data?.items?.find((i) => i.incident_ids.includes(incidentId));
    return fromInv?.id;
  }

  return (
    <div className="case-directory" id="case-directory">
      <div className="directory-heading">
        <div>
          <h3>Active demo investigations</h3>
          <p className="muted text-sm" style={{ margin: '2px 0 0' }}>
            Pre-registered municipal defect investigations with graph traceability
          </p>
        </div>
        <button
          className="text-button"
          type="button"
          onClick={() => {
            catalog.refresh();
            invList.refresh();
            page.refresh();
          }}
        >
          Refresh list
        </button>
      </div>

      {catalog.status === 'loading' && invList.status === 'loading' ? (
        <ReadMessage state={catalog} resourceName="case directory" retry={() => { catalog.refresh(); invList.refresh(); }} />
      ) : cases.length ? (
        <div className="registered-cases">
          {cases.map((c) => {
            const shortInv = formatShortIdentifier(c.investigation_id);
            const readableIssue = issueName(c.issue_type);

            return (
              <Link
                key={c.investigation_id + ':' + c.incident_id}
                className="registered-case"
                href={caseHref({ issue, incident: c.incident_id, investigation: c.investigation_id })}
              >
                <div className="case-card-top">
                  <span className="case-icon-title">
                    <Icon name="search" size={17} />
                    <strong>{readableIssue}</strong>
                  </span>
                  <span className="small-tag">SIMULATED</span>
                </div>

                <div className="case-card-body">
                  <p className="case-card-desc">
                    Investigation Case <span className="id-sub">{shortInv}</span>
                  </p>
                  <span className="stage-pill-mini">{translateStatus(c.stage)}</span>
                </div>

                <span className="category-link">
                  Open investigation <Icon name="arrow" size={14} />
                </span>
              </Link>
            );
          })}
        </div>
      ) : (
        <p className="directory-empty">No active investigations match this filter.</p>
      )}

      <div className="directory-heading" style={{ marginTop: '1.5rem' }}>
        <div>
          <h3>Reported civic incidents</h3>
          {page.data && <p className="muted text-sm" style={{ margin: '2px 0 0' }}>{page.data.total_count} matching records &bull; up to 10 per page</p>}
        </div>
      </div>

      {page.status !== 'ready' ? (
        <ReadMessage state={page} resourceName="incidents" retry={page.refresh} />
      ) : page.data?.items.length ? (
        <ul className="incident-list">
          {page.data.items.map((incident) => {
            const linkedId = getLinkedInvId(incident.id);
            const readableIssue = issueName(incident.issue_type);
            const shortInc = formatShortIdentifier(incident.id);

            return (
              <li key={incident.id}>
                <Link href={caseHref({ issue, incident: incident.id, investigation: linkedId })}>
                  <div className="incident-row-header">
                    <div className="incident-title-group">
                      <strong>{readableIssue} Incident</strong>
                      <span className="id-sub">{shortInc}</span>
                    </div>
                    <span className="status-tag">{translateStatus(incident.status)}</span>
                  </div>

                  <span className="incident-meta">
                    {displayTime(incident.started_at)} &bull; {incident.location_id ?? 'Civic location not specified'}
                  </span>

                  <span className="category-link">
                    {linkedId ? 'Open linked investigation' : 'View incident record'} <span aria-hidden="true">↗</span>
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      ) : (
        <p className="directory-empty">No incidents match this category.</p>
      )}

      {page.data && (
        <div className="pagination">
          <button
            type="button"
            className="button secondary"
            disabled={!cursor}
            onClick={() => pageTo()}
          >
            First page
          </button>
          <span>
            {page.data.items.length} shown &bull; {page.data.total_count} matching
          </span>
          <button
            type="button"
            className="button secondary"
            disabled={!page.data.next_cursor}
            onClick={() => pageTo(page.data!.next_cursor!)}
          >
            Next page
          </button>
        </div>
      )}

      {page.data?.truncated || page.data?.limitations?.length ? (
        <details className="resource-notes">
          <summary>List bounds and limitations</summary>
          {page.data.limitations?.map((text, index) => (
            <p key={index}>{text}</p>
          ))}
          {page.data.truncated && (
            <p>
              The backend marked this result as truncated. Narrow the request; this is not the complete
              source.
            </p>
          )}
        </details>
      ) : null}
    </div>
  );
}
