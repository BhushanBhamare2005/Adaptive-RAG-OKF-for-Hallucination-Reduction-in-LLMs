import { useState } from 'react';
import AnswerInput from '../components/analysis/AnswerInput';
import RiskScore from '../components/analysis/RiskScore';
import EvidenceViewer from '../components/analysis/EvidenceViewer';
import { analyzeAnswer } from '../services/analysisService';
import { AnalyzeResponse } from '../types';

const MODELS = ['baseline_rag', 'self_correction', 'adaptive_okf'];

export default function Analyze() {
  const [model, setModel] = useState('adaptive_okf');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [evidence, setEvidence] = useState('');
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    if (!answer.trim() || !evidence.trim()) {
      setError('Answer and evidence are required.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await analyzeAnswer({ model, question, answer, evidence });
      setResult(res);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Request failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2>Analyze Answer</h2>
      <p style={{ color: '#b8afc5', fontSize: '0.9rem' }}>
        The question is optional context; the current model scores the answer against the evidence.
      </p>
      <div className="card">
        <label style={{ display: 'block', marginBottom: '0.3rem', color: '#b8afc5' }}>
          Model
        </label>
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          style={{ padding: '0.5rem', marginBottom: '1rem' }}
        >
          {MODELS.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
        <AnswerInput label="Question (optional)" value={question} onChange={setQuestion} rows={2} />
        <AnswerInput label="Answer" value={answer} onChange={setAnswer} rows={4} />
        <AnswerInput label="Evidence" value={evidence} onChange={setEvidence} rows={4} />
        <button onClick={submit} disabled={loading}>
          {loading ? 'Analyzing…' : 'Analyze'}
        </button>
        {error && <div style={{ color: '#d946ef', marginTop: '0.5rem' }}>{error}</div>}
      </div>
      {result && (
        <div className="grid">
          <RiskScore score={result.risk_score} hallucinated={result.hallucinated} />
          <EvidenceViewer evidence={evidence} />
          <div className="card">
            <div style={{ fontSize: '0.85rem', color: '#b8afc5', marginBottom: 4 }}>
              Features
            </div>
            <ul style={{ margin: 0, paddingLeft: '1rem' }}>
              {result.features.map((f) => (
                <li key={f.name}>
                  {f.name}: {f.value.toFixed(3)}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
