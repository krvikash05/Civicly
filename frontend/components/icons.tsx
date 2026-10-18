export function Icon({ name, size = 20 }: { name: string; size?: number }) {
  const paths: Record<string, React.ReactNode> = {
    overview: <><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></>,
    search: <><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4.5 4.5"/></>,
    graph: <><circle cx="5" cy="6" r="3"/><circle cx="19" cy="5" r="3"/><circle cx="13" cy="19" r="3"/><path d="m8 6 8-1M6.5 8.5l5 8M17.8 7.7l-3.5 8.5"/></>,
    water: <><path d="M12 3c-2 4-7 7.5-7 12a7 7 0 0 0 14 0c0-4.5-5-8-7-12Z"/><path d="M9 16a3 3 0 0 0 3 3"/></>,
    road: <><path d="m7 3-4 18M17 3l4 18M12 3v4m0 3v4m0 3v4"/></>,
    waste: <><path d="M4 6h16M9 6V3h6v3M6 6l1 15h10l1-15M10 10v7m4-7v7"/></>,
    arrow: <><path d="M4 12h16m-6-6 6 6-6 6"/></>,
    shield: <><path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z"/><path d="m8 12 3 3 5-6"/></>,
    clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    file: <><path d="M14 3H5v18h14V8l-5-5Zm0 0v5h5M8 12h8m-8 4h5"/></>,
    layers: <><path d="m12 3 10 6-10 6L2 9l10-6Zm-10 12 10 6 10-6M2 12l10 6 10-6"/></>,
    help: <><circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 0 1 5 0c0 2-2.5 2-2.5 4m0 3v.2"/></>,
  };
  return <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">{paths[name] ?? paths.file}</svg>;
}
