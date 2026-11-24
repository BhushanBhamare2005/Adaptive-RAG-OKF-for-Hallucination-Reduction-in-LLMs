import { useEffect, useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import { getExplainModels, explainPrediction } from '../services/platformService';

export default function Explainability() {
  const [models, setModels] = useState<any[]>([]);
  const [model, setModel] = useState('adaptive_okf');
  const [answer, setAnswer] = useState('');
  const [evidence, setEvidence] = useState('');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  useEffect(() => { getExplainModels().then((data) => setModels(data.models || [])).catch(() => setModels([])); }, []);
  async function explain() {
    if (!answer.trim() || !evidence.trim()) { setError('Answer and evidence are required.'); return; }
    setError('');
    try { setResult(await explainPrediction(model, answer, evidence)); } catch (e: any) { setError(e?.response?.data?.detail || 'Explanation unavailable.'); }
  }
  return <div>
    <PageHeader eyebrow="Model interpretation" title="Explainability Center" description="Inspect real model-native feature importance for current predictions." />
    {error && <div className="alert error">{error}</div>}
    <div className="form-grid"><section className="panel"><label className="field-label">Model<select value={model} onChange={(e) => setModel(e.target.value)}>{models.map((item) => <option key={item.name} value={item.name}>{item.name}</option>)}</select></label><label className="field-label">Answer<textarea rows={5} value={answer} onChange={(e) => setAnswer(e.target.value)} /></label><label className="field-label">Evidence<textarea rows={5} value={evidence} onChange={(e) => setEvidence(e.target.value)} /></label><button className="button primary full" onClick={explain}>Calculate explanation</button></section>
    <section className="panel"><div className="panel-header"><div><span className="eyebrow">Feature contributions</span><h2>Decision factors</h2></div></div>{result ? result.available ? <><div className="probability-row"><span>Hallucination probability</span><strong>{(result.probability * 100).toFixed(1)}%</strong></div>{result.explanations.map((item: any) => <div className="explanation-row" key={item.feature}><div><span>{item.feature}</span><small>value {item.value.toFixed(3)}</small></div><strong className={item.contribution >= 0 ? 'success-text' : 'danger-text'}>{item.contribution >= 0 ? '+' : ''}{item.contribution.toFixed(3)}</strong></div>)}</> : <div className="empty-state">{result.reason}</div> : <div className="empty-state">No explanation calculated.</div>}</section></div>
  </div>;
}
