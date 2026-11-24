import { useEffect, useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import { runAEVL, getAEVLRuns } from '../services/platformService';

export default function AEVL() {
  const [answer, setAnswer] = useState('');
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState<any>(null);
  const [runs, setRuns] = useState<any[]>([]);
  const [error, setError] = useState('');
  async function load() { getAEVLRuns().then((data) => setRuns(data.runs || [])).catch(() => setRuns([])); }
  useEffect(() => { load(); }, []);
  async function execute() {
    if (!answer.trim() || !question.trim()) { setError('Question and answer are required.'); return; }
    setError('');
    try { setResult(await runAEVL(answer, question)); await load(); } catch (e: any) { setError(e?.response?.data?.detail || 'AEVL run failed.'); }
  }
  return <div>
    <PageHeader eyebrow="Adaptive Evidence Verification Loop" title="AEVL Self-Repair Center" description="Detect unsupported claims, expand evidence and determine whether repair or abstention is justified." />
    {error && <div className="alert error">{error}</div>}
    <div className="form-grid">
      <section className="panel"><label className="field-label">Question<input value={question} onChange={(e) => setQuestion(e.target.value)} /></label><label className="field-label">Answer<textarea rows={7} value={answer} onChange={(e) => setAnswer(e.target.value)} /></label><button className="button primary full" onClick={execute}>Run verification loop</button></section>
      <section className="panel"><div className="panel-header"><div><span className="eyebrow">Outcome</span><h2>Repair timeline</h2></div></div>{result ? <><div className={`verdict ${result.abstained ? 'danger' : 'success'}`}>{result.abstained ? 'Abstained — unresolved evidence' : 'Verified'}</div>{result.loops?.map((loop: any) => <article className="loop-card" key={loop.loop}><strong>Loop {loop.loop}</strong><span>{loop.unresolved_count} unresolved claims</span>{loop.claims.map((claim: any) => <div className="loop-claim" key={claim.claim_id}><span>{claim.claim_text}</span><small>{claim.classification}</small></div>)}</article>)}</> : <div className="empty-state">Run AEVL to inspect verification iterations.</div>}</section>
    </div>
  </div>;
}
