import { useEffect, useState } from 'react';
import { isAxiosError } from 'axios';
import { getComparison, trainModels } from '../services/experimentService';
import { ComparisonMap } from '../types';

export default function Experiments() {
  const [comparison, setComparison] = useState<ComparisonMap>({});
  const [error, setError] = useState<string | null>(null);
  const [training, setTraining] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    getComparison()
      .then(setComparison)
      .catch(() => setError('Could not load experiment results. Is the backend running?'));
  }, []);

  async function runTraining() {
    setTraining(true);
    setError(null);
    setMessage(null);
    try {
      const result = await trainModels();
      setComparison(result.comparison);
      setMessage('Training and evaluation completed successfully.');
    } catch (requestError) {
      setError(
        isAxiosError<{ detail?: string }>(requestError)
          ? requestError.response?.data?.detail ??
              'Training failed. Check that the backend and datasets are available.'
          : 'Training failed. Check that the backend and datasets are available.'
      );
    } finally {
      setTraining(false);
    }
  }

  const rows = Object.entries(comparison);

  return (
    <div>
      <h2>Experiment Results</h2>
      <div className="card">
        <p>Train all three models on the available datasets and evaluate them on a held-out split.</p>
        <button onClick={runTraining} disabled={training}>
          {training ? 'Training models…' : 'Train and evaluate'}
        </button>
        {message && <div style={{ color: '#00e5a0', marginTop: '0.75rem' }}>{message}</div>}
      </div>
      {error && <div className="card" style={{ color: '#d946ef' }}>{error}</div>}
      {rows.length === 0 && !error && <div className="card">No results yet. Start training above.</div>}
      {rows.length > 0 && (
        <div className="card">
          <table>
            <thead>
              <tr>
                <th>Model</th>
                <th>Accuracy</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1</th>
                <th>ROC-AUC</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(([model, m]) => (
                <tr key={model}>
                  <td>{model}</td>
                  <td>{m.accuracy.toFixed(3)}</td>
                  <td>{m.precision.toFixed(3)}</td>
                  <td>{m.recall.toFixed(3)}</td>
                  <td>{m.f1.toFixed(3)}</td>
                  <td>{m.roc_auc != null ? m.roc_auc.toFixed(3) : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
