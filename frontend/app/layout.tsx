import type { Metadata } from 'next';
import { Shell } from '../components/shell';
import './globals.css';
import {DemoProvider} from '../components/demo-connection';

export const metadata: Metadata = {
  title: { default: 'Civicly · Overview', template: '%s · Civicly' },
  description: 'Connected evidence. Informed civic action. Investigate recurring civic problems with graph-backed evidence.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body><DemoProvider><Shell>{children}</Shell></DemoProvider></body></html>;
}
