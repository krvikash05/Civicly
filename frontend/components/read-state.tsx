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
  if (state.status === 'ready') return null;

  if (state.status === 'loading') {
    return (
      <div className="read-message read-loading" role="status">
        <span className="read-loading-dot" aria-hidden="true" />
        <p>{state.message.startsWith('Connecting')?'Connecting to the demo workspace…':`Loading ${resourceName}…`}</p>
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

    const code=state.errorCode;
    if(code==='UNAUTHORIZED'){
      categoryTitle='Reconnect your demo session';
    }else if(code==='PERMISSION_DENIED'){
      categoryTitle='This role cannot access this record';isAccessDenied=true;
    }else if(code==='RECOVERY_REQUIRED'||code==='WRITE_OUTCOME_UNKNOWN'){
      categoryTitle='Operator review required';isPrerequisite=true;
      userFriendlyMsg='The previous operation may have been saved. Keep its original request key and ask the presenter to check the result; do not submit it as a new action.';
    }else if(code==='CONFLICT'){
      categoryTitle='The record changed';
      userFriendlyMsg='Reload the current record before continuing. A conflict does not mean that an earlier action failed to save.';
    }else if(code==='DEPENDENCY_BLOCKED'){
      categoryTitle='A required source or workflow check is unavailable';
    }else if(code==='NOT_FOUND'){
      categoryTitle='Requested record not returned';
      userFriendlyMsg=`This ${resourceName} could not be retrieved. The loaded result does not prove that no related records exist.`;
    }else if(['EXTERNAL_UNAVAILABLE','GRAPH_UNAVAILABLE','NETWORK_ERROR'].includes(code??'')){
      categoryTitle='Data connection interrupted';
      userFriendlyMsg='The data service could not be reached. Ask the presenter to check it, then reload these records.';
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

  return <p className="muted text-sm" role="status">{state.message || 'These records are unavailable. Reconnect the demo session to continue.'}</p>;
}
