'use client';

import React, { useState } from 'react';

export interface TechDetailItem {
  label: string;
  value: React.ReactNode;
  rawString?: string;
  isCopyable?: boolean;
}

interface TechnicalDetailsProps {
  title?: string;
  items?: TechDetailItem[];
  children?: React.ReactNode;
  defaultOpen?: boolean;
}

export function TechnicalDetails({
  title = 'Technical details',
  items = [],
  children,
  defaultOpen = false,
}: TechnicalDetailsProps) {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const handleCopy = async (key: string, textToCopy: string) => {
    try {
      if (typeof navigator !== 'undefined' && navigator.clipboard) {
        await navigator.clipboard.writeText(textToCopy);
        setCopiedKey(key);
        setTimeout(() => setCopiedKey(null), 2000);
      }
    } catch {
      // Fallback for environments where clipboard is disabled
      setCopiedKey(null);
    }
  };

  return (
    <details className="technical-details" open={defaultOpen}>
      <summary className="tech-summary">
        <span className="tech-toggle-icon">▸</span>
        <span className="tech-title">{title}</span>
      </summary>
      <div className="tech-content">
        {items.length > 0 && (
          <dl className="tech-dl">
            {items.map((item, idx) => {
              const strVal = item.rawString || (typeof item.value === 'string' ? item.value : '');
              const canCopy = item.isCopyable ?? Boolean(strVal);
              const isCopied = copiedKey === `${item.label}-${idx}`;

              return (
                <div key={idx} className="tech-row">
                  <dt className="tech-label">{item.label}:</dt>
                  <dd className="tech-value">
                    <span className="tech-value-inner">{item.value}</span>
                    {canCopy && strVal && (
                      <button
                        type="button"
                        className="tech-copy-btn"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          handleCopy(`${item.label}-${idx}`, strVal);
                        }}
                        aria-label={`Copy ${item.label} to clipboard`}
                        title="Copy to clipboard"
                      >
                        {isCopied ? 'Copied' : 'Copy'}
                      </button>
                    )}
                  </dd>
                </div>
              );
            })}
          </dl>
        )}
        {children}
      </div>
    </details>
  );
}

export function CopyableIdentifier({
  id,
  label,
  shortDisplay,
}: {
  id: string;
  label?: string;
  shortDisplay?: string;
}) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      if (typeof navigator !== 'undefined' && navigator.clipboard) {
        await navigator.clipboard.writeText(id);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } catch {
      setCopied(false);
    }
  };

  return (
    <span className="copyable-identifier" title={`Full ID: ${id}`}>
      <code className="id-code">{shortDisplay || id}</code>
      <button
        type="button"
        className="id-copy-btn"
        onClick={handleCopy}
        aria-label={`Copy ${label || 'identifier'} ${id}`}
      >
        {copied ? '✓' : 'Copy'}
      </button>
    </span>
  );
}
