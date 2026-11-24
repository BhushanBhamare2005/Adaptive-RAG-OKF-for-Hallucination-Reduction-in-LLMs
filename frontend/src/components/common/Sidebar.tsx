import { NavLink } from 'react-router-dom';

const links = [
  { to: '/', label: 'Overview', icon: '▦' },
  { to: '/knowledge', label: 'Knowledge Base', icon: 'DB' },
  { to: '/upload', label: 'Upload Center', icon: '↑' },
  { to: '/rag', label: 'AI Chat', icon: 'AI' },
  { to: '/claims', label: 'Claim Studio', icon: '✓' },
  { to: '/adaptive-okf', label: 'Adaptive OKF', icon: '◉' },
  { to: '/aevl', label: 'AEVL Repair', icon: '↻' },
  { to: '/conflicts', label: 'Conflicts', icon: '≠' },
  { to: '/models', label: 'Model Lab', icon: 'MX' },
  { to: '/explainability', label: 'Explainability', icon: 'X' },
  { to: '/audit', label: 'Audit Logs', icon: '⌁' },
  { to: '/settings', label: 'Settings', icon: '⚙' },
];

export default function Sidebar({ collapsed }: { collapsed: boolean }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark">A</span>
        {!collapsed && <div><strong>Adaptive OKF</strong><small>Verification Platform</small></div>}
      </div>
      <nav className="sidebar-nav">
      {links.map((l) => (
        <NavLink
          key={l.to}
          to={l.to}
          className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
          title={collapsed ? l.label : undefined}
        >
          <span className="nav-icon">{l.icon}</span>
          {!collapsed && <span>{l.label}</span>}
        </NavLink>
      ))}
      </nav>
      <div className="sidebar-footer">
        {!collapsed && <><span className="status-dot" /> System operational</>}
      </div>
    </aside>
  );
}
