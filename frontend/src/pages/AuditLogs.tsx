import { useEffect, useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import { getAuditEvents } from '../services/platformService';

export default function AuditLogs() {
  const [events, setEvents] = useState<any[]>([]);
  const [error, setError] = useState('');
  useEffect(() => { getAuditEvents().then((data) => setEvents(data.events || [])).catch((e) => setError(e?.response?.data?.detail || 'Audit logs unavailable.')); }, []);
  return <div>
    <PageHeader eyebrow="Governance" title="Audit Logs and Monitoring" description="Immutable operational history for document and verification actions." />
    {error && <div className="alert error">{error}</div>}
    <section className="panel">{events.length === 0 ? <div className="empty-state">No audit events have been recorded.</div> : <div className="table-wrap"><table><thead><tr><th>Time</th><th>Event</th><th>Entity</th><th>Action</th><th>Actor</th></tr></thead><tbody>{events.map((event) => <tr key={event.id}><td>{new Date(event.timestamp).toLocaleString()}</td><td>{event.event_type}</td><td>{event.entity_type}</td><td><span className="badge indexed">{event.action}</span></td><td>{event.actor}</td></tr>)}</tbody></table></div>}</section>
  </div>;
}
