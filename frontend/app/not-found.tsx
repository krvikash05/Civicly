import Link from 'next/link';
export default function NotFound() { return <div className="empty-state"><h1>Page not found</h1><p>Return to the workspace to continue.</p><Link className="button primary" href="/">Back to overview</Link></div>; }
