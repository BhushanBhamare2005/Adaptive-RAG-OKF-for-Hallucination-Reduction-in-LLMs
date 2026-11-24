import { useEffect, useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import { getAdaptiveConfig, evaluateAdaptive } from '../services/platformService';

export default function AdaptiveOKF() {
  const [config, setConfig] = useState<any>(null);
  const [answer, setAnswer] = useState('');
  const [evidence, setEvidence] = useState('');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  useEffect(() => { getAdaptiveConfig().then(setConfig).catch(() => setError('Adaptive OKF configuration is unavailable.')); }, []);
  async function evaluate() {
    if (!answer.trim() || !evidence.trim()) { setError('Answer and evidence are required.'); return; }
    setError('');
    try { setResult(await evaluateAdaptive({ model: 'adaptive_okf', answer, evidence })); } catch (e: any) { setError(e?.response?.data?.detail || 'Evaluation failed.'); }
  }
  return <div>
    <PageHeader eyebrow="Risk engine" title="Adaptive OKF Engine" description="Evidence-aware risk evaluation using persisted thresholds and the existing Adaptive OKF model." />
    {error && <div className="alert error">{error}</div>}
    <div className="form-grid">
      <section className="panel"><div className="panel-header"><div><span className="eyebrow">Decision inputs</span><h2>Evaluate evidence</h2></div></div><label className="field-label">Answer<textarea rows={5} value={answer} onChange={(e) => setAnswer(e.target.value)} /></label><label className="field-label">Evidence<textarea rows={5} value={evidence} onChange={(e) => setEvidence(e.target.value)} /></label><button className="button primary full" onClick={evaluate}>Run verification</button></section>
      <section className="panel"><div className="panel-header"><div><span className="eyebrow">Live decision</span><h2>Risk output</h2></div></div>
        {result ? <><div className="risk-gauge"><strong>{(result.risk_score * 100).toFixed(1)}%</strong><span>{result.decision}</span></div><div className="feature-list">{result.features?.map((feature: any) => <div key={feature.name}><span>{feature.name}</span><strong>{feature.value.toFixed(3)}</strong></div>)}</div></> : <div className="empty-state">Run an evaluation to calculate risk.</div>}
        {config && <div className="config-summary"><span>Configured threshold</span><strong>{config.threshold}</strong></div>}
      </section>
    </div>
  </div>;
}
