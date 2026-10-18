'use client';

import React from 'react';
import type { ReadState } from './use-read';
import { TechnicalDetails } from './technical-details';

interface ReadMessageProps {
  state: ReadState<unknown>;
  resourceName?: string;
  retry?: () => void;
}

export function ReadMessage({ state, resourceName = 'resource', retry }: ReadMessageProps) {
  if (state.status === 'idle') return null;

  if (state.status === 'loading') {
    return (
      <div className="read-message read-loading" role="status">
        <span className="read-spinner" aria-hidden="true">⏳</span>
        <p>Loading {resourceName} details…</p>
      </div>
    );
  }

  if (state.status === 'error') {
    // Categorize error meaningfully
    const rawMsg = state.message || '';
    let categoryTitle = 'Records could not be loaded';
    let userFriendlyMsg = rawMsg;
    let isPrerequisite = false;
    let isAccessDenied = false;

    if (rawMsg.includes('401') || rawMsg.includes('UNAUTHORIZED') || rawMsg.includes('Authentication')) {
      categoryTitle = 'Authentication required';
      userFriendlyMsg = 'Your session has expired or authentication is not established. Reconnect your session to proceed.';
    } else if (rawMsg.includes('403') || rawMsg.includes('FORBIDDEN') || rawMsg.includes('Permission')) {
      categoryTitle = 'Access is denied';
      isAccessDenied = true;
      userFriendlyMsg = 'Your active operator role does not have authorization to view or modify this resource.';
    } else if (rawMsg.includes('409') || rawMsg.includes('DEPENDENCY_BLOCKED') || rawMsg.includes('PREREQUISITE')) {
      categoryTitle = 'A prerequisite is unmet';
      isPrerequisite = true;
      userFriendlyMsg = 'This record depends on prior workflow stages completing first. Complete previous investigations or approvals before this can be viewed.';
    } else if (rawMsg.includes('404') || rawMsg.includes('NOT_FOUND')) {
      categoryTitle = 'No records exist';
      userFriendlyMsg = `The requested ${resourceName} was not found in the civic ledger.`;
    } else if (rawMsg.includes('UNAVAILABLE') || rawMsg.includes('503')) {
      categoryTitle = 'Service temporarily unavailable';
      userFriendlyMsg = 'The civic data service is currently busy or reindexing. You may try refreshing the query.';
    }

    const techItems = [
      ...(state.requestId ? [{ label: 'Request ID', value: <code>{state.requestId}</code>, rawString: state.requestId }] : []),
      { label: 'Raw error message', value: <span>{rawMsg}</span>, rawString: rawMsg },
      { label: 'Resource targeted', value: <span>{resourceName}</span>, rawString: resourceName },
    ];

    return (
      <div
        className={`read-message read-error ${isPrerequisite ? 'read-prerequisite' : ''} ${isAccessDenied ? 'read-forbidden' : ''}`}
        role="alert"
      >
        <div className="read-error-body">
          <div className="read-error-header">
            <span className="read-error-icon" aria-hidden="true">
              {isPrerequisite ? 'ℹ' : isAccessDenied ? '🔒' : '⚠'}
            </span>
            <strong>{categoryTitle}</strong>
          </div>
          <p className="read-error-text">{userFriendlyMsg}</p>

          <TechnicalDetails
            title="Technical error details"
            items={techItems}
          />
        </div>

        {retry && !isPrerequisite && !isAccessDenied && (
          <button type="button" className="button secondary small" onClick={retry}>
            Try again
          </button>
        )}
      </div>
    );
  }

  return null;
}
