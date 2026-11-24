import { useEffect, useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import KpiCard from '../components/dashboard/KpiCard';
import { getOverview } from '../services/platformService';

export default function Overview() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    getOverview().then(setData).catch((e) => setError(e?.response?.data?.detail || 'Overview could not be loaded.'));
  }, []);
  return (
    <div>
      <PageHeader eyebrow="Command center" title="Verification Overview" description="Live knowledge, retrieval and hallucination verification activity." />
      {error && <div className="alert error">{error}</div>}
      {!data && !error && <div className="skeleton-grid">{[1,2,3,4].map((n) => <div className="skeleton" key={n}/>)}</div>}
      {data && <>
        <div className="kpi-grid">
          <KpiCard label="Indexed documents" value={data.total_documents} detail={`${data.indexed_chunks} indexed chunks`} tone="blue"/>
          <KpiCard label="Queries processed" value={data.total_queries} detail="Persisted RAG requests" tone="violet"/>
          <KpiCard label="Verified answers" value={`${data.verified_answer_percentage}%`} detail={`${data.open_conflicts} open conflicts`} tone="teal"/>
          <KpiCard label="Average risk" value={`${(data.average_risk_score * 100).toFixed(1)}%`} detail={`${data.abstention_percentage}% abstained`} tone="orange"/>
          <KpiCard label="Successful repairs" value={`${data.successful_repair_rate}%`} detail="Answers repaired through AEVL" tone="green"/>
        </div>
        <div className="dashboard-grid">
          <section className="panel">
            <div className="panel-header"><div><span className="eyebrow">Live feed</span><h2>Recent verification activity</h2></div></div>
            {data.recent_activity?.length ? data.recent_activity.map((item: any) => (
              <div className="activity-row" key={item.id}>
                <span className={`activity-icon ${item.abstained ? 'danger' : 'success'}`}>{item.abstained ? '!' : '✓'}</span>
                <div><strong>{item.question}</strong><small>{item.abstained ? 'Abstained' : 'Verified'} · risk {(item.risk_score * 100).toFixed(1)}%</small></div>
              </div>
            )) : <div className="empty-state">No verification activity yet.</div>}
          </section>
          <section className="panel">
            <div className="panel-header"><div><span className="eyebrow">Provider</span><h2>System status</h2></div></div>
            <div className="status-list">
              <div><span>LLM provider</span><strong className={data.provider?.status === 'configured' ? 'success-text' : 'warning-text'}>{data.provider?.status || 'unknown'}</strong></div>
              <div><span>Open conflicts</span><strong>{data.open_conflicts}</strong></div>
              <div><span>Pending feedback</span><strong>{data.pending_feedback}</strong></div>
              <div><span>Hallucination rate</span><strong>{data.hallucination_detection_rate}%</strong></div>
            </div>
          </section>
        </div>
      </>}
    </div>
  );
}
