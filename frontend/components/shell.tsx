'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Icon } from './icons';
import { DemoStatus } from './demo-connection';
import { ScenarioJourneyGuide } from './scenario-journey-guide';
import { RoleGovernanceModal } from './role-governance-modal';

export function Shell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const [isJourneysOpen, setIsJourneysOpen] = useState(false);
  const [isRolesOpen, setIsRolesOpen] = useState(false);

  return (
    <>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>

      <aside className="sidebar" aria-label="Application sidebar">
        <Link className="brand" href="/" aria-label="Civicly home">
          <span className="brand-mark">
            <Icon name="graph" size={25} />
          </span>
          <span className="brand-wordmark">
            <span className="brand-name">Civicly<span className="brand-dot">.</span></span>
            <span className="brand-powered">Powered by FalkorDB</span>
          </span>
        </Link>

        <div className="district">
          <span className="district-icon">
            <Icon name="layers" />
          </span>
          <div>
            <strong>Demo City</strong>
            <small>Synthetic municipal district</small>
          </div>
        </div>

        <p className="nav-label">WORKSPACE</p>
        <nav aria-label="Main navigation">
          {[
            ['/', 'overview', 'Overview'],
            ['/investigations', 'search', 'Investigations'],
          ].map(([href, icon, label]) => (
            <Link
              key={href}
              href={href}
              className={`nav-link ${path === href ? 'active' : ''}`}
              aria-current={path === href ? 'page' : undefined}
            >
              <Icon name={icon} />
              {label}
              {path === href && <span className="active-dot" />}
            </Link>
          ))}
        </nav>

        <p className="nav-label" style={{ marginTop: 20 }}>
          EXPLORE &amp; GOVERNANCE
        </p>
        <div className="sidebar-action-group">
          <button
            type="button"
            className="sidebar-action-btn"
            onClick={() => setIsJourneysOpen(true)}
            aria-haspopup="dialog"
          >
            <Icon name="layers" size={16} />
            <span>Scenario Journeys (S01–S12)</span>
          </button>

          <button
            type="button"
            className="sidebar-action-btn"
            onClick={() => setIsRolesOpen(true)}
            aria-haspopup="dialog"
          >
            <Icon name="check" size={16} />
            <span>Roles &amp; permissions</span>
          </button>
        </div>

        <div className="sidebar-note">
          <Icon name="graph" />
          <strong>Connected by evidence.</strong>
          <p>Follow the relationships behind each investigation.</p>
          <Link href="/investigations#graph-evidence">
            Explore graph evidence <span aria-hidden="true">↗</span>
          </Link>
        </div>

        <div className="sidebar-bottom">
          <span className="simulation-dot" /> Simulated environment{' '}
          <details>
            <summary>About this workspace</summary>
            <p>
              Civicly investigates recurring civic problems using FalkorDB, agent tools and
              attributed evidence. A host-configured demo identity connects automatically.
              Approvals and departmental actions remain subject to backend authorization.
            </p>
          </details>
        </div>
      </aside>

      <div className="application">
        <header className="topbar">
          <div className="topbar-left">
            <span>
              Workspace <span className="breadcrumb-separator">/</span>{' '}
              <strong>{path === '/' ? 'Overview' : 'Investigations'}</strong>
            </span>
          </div>
          <div className="topbar-right">
            <button
              type="button"
              className="topbar-action-pill"
              onClick={() => setIsJourneysOpen(true)}
              title="Browse 12 pre-seeded demonstration scenarios"
            >
              <Icon name="layers" size={14} /> Scenarios
            </button>
            <button
              type="button"
              className="topbar-action-pill"
              onClick={() => setIsRolesOpen(true)}
              title="Inspect municipal operator roles & authority boundaries"
            >
              <Icon name="check" size={14} /> Roles
            </button>
            <DemoStatus />
          </div>
        </header>

        <main id="main-content" tabIndex={-1}>
          {children}
        </main>

        <footer className="footer">
          <span>
            Civicly <span aria-hidden="true">/</span> Connected evidence. Informed action.
          </span>
          <span>FalkorDB-powered investigation</span>
        </footer>
      </div>

      {/* Scenario Journeys Interactive Modal */}
      <ScenarioJourneyGuide
        isOpen={isJourneysOpen}
        onClose={() => setIsJourneysOpen(false)}
      />

      {/* Municipal Role Governance Modal */}
      <RoleGovernanceModal
        isOpen={isRolesOpen}
        onClose={() => setIsRolesOpen(false)}
      />
    </>
  );
}

