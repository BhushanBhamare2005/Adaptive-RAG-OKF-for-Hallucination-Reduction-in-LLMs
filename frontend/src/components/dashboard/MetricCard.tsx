export default function MetricCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint?: string;
}) {
  return (
    <div className="card">
      <div style={{ fontSize: '0.85rem', color: '#b8afc5' }}>{label}</div>
      <div style={{ fontSize: '1.6rem', fontWeight: 700 }}>{value}</div>
      {hint && <div style={{ fontSize: '0.75rem', color: '#81748f' }}>{hint}</div>}
    </div>
  );
}
