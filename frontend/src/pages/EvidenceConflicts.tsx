import { useEffect, useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import { getConflicts, detectConflicts, resolveConflict } from '../services/platformService';

export default function EvidenceConflicts() {
  const [conflicts, setConflicts] = useState<any[]>([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  async function load() { try { setConflicts((await getConflicts()).conflicts || []); } catch (e: any) { setError(e?.response?.data?.detail || 'Could not load conflicts.'); } }
  useEffect(() => { load(); }, []);
  async function detect() { setError(''); try { const data = await detectConflicts(); setMessage(`${data.detected} conflicts detected.`); await load(); } catch (e: any) { setError(e?.response?.data?.detail || 'Conflict detection failed.'); } }
  async function resolve(id: string) { await resolveConflict(id, { resolution_status: 'resolved', resolved_by: 'human-reviewer', resolution_notes: 'Resolved from the evidence conflict explorer.' }); await load(); }
  return <div>
    <PageHeader eyebrow="Contradiction analysis" title="Evidence Conflict Explorer" description="Compare conflicting documents and persist human resolutions." action={<button className="button primary" onClick={detect}>Detect conflicts</button>} />
    {message && <div className="alert success">{message}</div>}{error && <div className="alert error">{error}</div>}
    {conflicts.length === 0 ? <div className="panel empty-state">No evidence conflicts have been detected.</div> : <div className="conflict-grid">{conflicts.map((conflict) => <article className="panel conflict-card" key={conflict.id}><div className="claim-head"><span className={`severity ${conflict.severity}`}>{conflict.severity}</span><span className="badge">{conflict.resolution_status}</span></div><h3>{conflict.topic_key}</h3><p>{conflict.contradiction_summary}</p><div className="conflict-sources"><div><span>Source A</span><p>{conflict.excerpt_a}</p></div><div><span>Source B</span><p>{conflict.excerpt_b}</p></div></div>{conflict.resolution_status === 'open' && <button className="button secondary" onClick={() => resolve(conflict.id)}>Resolve conflict</button>}</article>)}</div>}
  </div>;
}
