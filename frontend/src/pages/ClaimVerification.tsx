import { useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import { verifyAnswer } from '../services/platformService';

export default function ClaimVerification() {
  const [answer, setAnswer] = useState('');
  const [claims, setClaims] = useState<any[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function verify() {
    if (!answer.trim()) { setError('Enter an answer to verify.'); return; }
    setBusy(true); setError('');
    try { const result = await verifyAnswer(answer.trim()); setClaims(result.claims || []); } catch (e: any) { setError(e?.response?.data?.detail || 'Verification failed.'); }
    finally { setBusy(false); }
  }
  return <div>
    <PageHeader eyebrow="Claim-level NLI" title="Claim Verification Studio" description="Decompose answers and verify each factual claim against retrieved evidence." />
    {error && <div className="alert error">{error}</div>}
    <section className="panel verify-input"><label className="field-label">Answer text<textarea value={answer} onChange={(e) => setAnswer(e.target.value)} rows={5} placeholder="Paste an answer to analyze..."/></label><button className="button primary" disabled={busy} onClick={verify}>{busy ? 'Verifying...' : 'Verify claims'}</button></section>
    <div className="claims-list">{claims.length === 0 ? <div className="empty-state">Claims and evidence classifications will appear here.</div> : claims.map((claim) => <article className="claim-card" key={claim.id}><div className="claim-head"><span className={`badge ${claim.classification}`}>{claim.classification.replace('_', ' ')}</span><strong>{(claim.risk_score * 100).toFixed(1)}% risk</strong></div><p>{claim.claim_text}</p><div className="claim-meta">Confidence {(claim.confidence * 100).toFixed(1)}%</div></article>)}</div>
  </div>;
}
