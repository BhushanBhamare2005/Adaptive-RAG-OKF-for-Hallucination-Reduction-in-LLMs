import { useEffect, useState } from 'react';
import { getDatasetSample, getDatasetSummary } from '../services/experimentService';
import { DataRecord, DatasetSummary } from '../types';

export default function DatasetExplorer() {
  const [summary, setSummary] = useState<DatasetSummary | null>(null);
  const [sample, setSample] = useState<DataRecord[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getDatasetSummary(), getDatasetSample(10)])
      .then(([datasetSummary, records]) => {
        setSummary(datasetSummary);
        setSample(records);
      })
      .catch(() => setError('Could not load the datasets. Is the backend running?'));
  }, []);

  return (
    <div>
      <h2>Dataset Explorer</h2>
      {error && <div className="card" style={{ color: '#d946ef' }}>{error}</div>}
      {summary && (
        <div className="grid">
          <div className="card">
            <div style={{ color: '#b8afc5', fontSize: '0.85rem' }}>Total</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{summary.total}</div>
          </div>
          {Object.entries(summary.sources).map(([src, count]) => (
            <div className="card" key={src}>
              <div style={{ color: '#b8afc5', fontSize: '0.85rem' }}>{src}</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{count}</div>
            </div>
          ))}
        </div>
      )}
      <h3>Sample Records</h3>
      {sample.map((r, i) => (
        <div className="card" key={i}>
          <div style={{ color: '#b8afc5', fontSize: '0.8rem' }}>
            {r.source} · label={r.label === 1 ? 'hallucinated' : 'grounded'}
          </div>
          <div style={{ marginTop: 4 }}>
            <strong>Q:</strong> {r.question}
          </div>
          <div>
            <strong>A:</strong> {r.answer}
          </div>
          <div>
            <strong>E:</strong> {r.evidence || 'Not supplied by this dataset'}
          </div>
        </div>
      ))}
    </div>
  );
}
