import type { Metadata } from 'next';
import { Suspense } from 'react';
import { InvestigationWorkspace } from '../../components/investigation-workspace';

export const metadata: Metadata = { title: 'Investigations' };

export default function Investigations() {
  return (
    <Suspense fallback={<div className="loading-workspace">Loading investigations workspace…</div>}>
      <InvestigationWorkspace />
    </Suspense>
  );
}
