export default function Loader({ label = 'Loading…' }: { label?: string }) {
  return <div style={{ padding: '1rem', color: '#b8afc5' }}>{label}</div>;
}
