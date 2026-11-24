import { useEffect, useState } from 'react';
import MetricCard from '../components/dashboard/MetricCard';
import PerformanceChart from '../components/dashboard/PerformanceChart';
import SystemStatus from '../components/dashboard/SystemStatus';
import { getComparison, getDatasetSummary } from '../services/experimentService';
import { ComparisonMap } from '../types';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const [comparison, setComparison] = useState<ComparisonMap>({});
  const [total, setTotal] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getComparison(), getDatasetSummary()])
      .then(([results, summary]) => {
        setComparison(results);
        setTotal(summary.total);
      })
      .catch(() => setError('Could not load dashboard data. Is the backend running?'));
  }, []);

  const chartData = Object.entries(comparison).map(([model, m]) => ({ model, ...m }));
  const best = chartData.reduce<(typeof chartData)[number] | null>(
    (current, candidate) => (!current || candidate.f1 > current.f1 ? candidate : current),
    null
  );

  return (
    <div>
      <h2>Dashboard</h2>
      <div className="grid">
        <MetricCard label="Normalized Examples" value={total} hint="From the raw datasets" />
        <MetricCard
          label="Best Model"
          value={best?.model ?? '—'}
          hint={best ? `F1 = ${best.f1.toFixed(3)}` : 'Train from Experiments'}
        />
        <SystemStatus />
      </div>
      {error && <div className="card" style={{ color: '#d946ef' }}>{error}</div>}
      <h3 style={{ marginTop: '2rem' }}>Model Comparison</h3>
      {chartData.length === 0 ? (
        <div className="card">
          No comparison yet. <Link to="/experiments">Train and evaluate the models</Link>.
        </div>
      ) : (
        <PerformanceChart data={chartData} />
      )}
    </div>
  );
}
