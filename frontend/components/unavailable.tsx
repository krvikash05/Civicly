import { Icon } from './icons';
export function Unavailable({ title, children, icon = 'layers' }: { title: string; children: React.ReactNode; icon?: string }) {
  return <div className="empty-state"><span className="empty-icon"><Icon name={icon} size={27}/></span><h3>{title}</h3><p>{children}</p><span className="quiet-tag">Data unavailable</span></div>;
}
