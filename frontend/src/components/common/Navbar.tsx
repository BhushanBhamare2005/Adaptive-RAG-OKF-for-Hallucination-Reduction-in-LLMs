export default function Navbar({ collapsed, onToggle }: { collapsed: boolean; onToggle: () => void }) {
  return (
    <header className="topbar">
      <button className="icon-button" type="button" onClick={onToggle} aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}>
        {collapsed ? '›' : '‹'}
      </button>
      <div className="topbar-search">Search documents, queries, or claims...</div>
      <div className="topbar-actions">
        <button className="icon-button" type="button" title="Notifications">◦</button>
        <div className="avatar">AK</div>
      </div>
    </header>
  );
}
