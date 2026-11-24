export default function KpiCard({
  label,
  value,
  detail,
  tone = 'blue',
}: {
  label: string;
  value: string | number;
  detail: string;
  tone?: 'blue' | 'violet' | 'teal' | 'green' | 'orange';
}) {
  return (
    <article className={`kpi-card tone-${tone}`}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      <div className="kpi-detail">{detail}</div>
    </article>
  );
}
