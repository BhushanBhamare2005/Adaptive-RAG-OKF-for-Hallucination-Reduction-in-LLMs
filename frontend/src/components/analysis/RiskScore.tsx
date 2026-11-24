export default function RiskScore({
  score,
  hallucinated,
}: {
  score: number;
  hallucinated: boolean;
}) {
  const color = hallucinated ? '#d946ef' : '#00e5a0';
  return (
    <div className="card">
      <div style={{ fontSize: '0.85rem', color: '#b8afc5' }}>Hallucination Risk</div>
      <div style={{ fontSize: '2rem', fontWeight: 700, color }}>
        {(score * 100).toFixed(1)}%
      </div>
      <div style={{ color }}>{hallucinated ? 'Likely hallucinated' : 'Likely grounded'}</div>
    </div>
  );
}
