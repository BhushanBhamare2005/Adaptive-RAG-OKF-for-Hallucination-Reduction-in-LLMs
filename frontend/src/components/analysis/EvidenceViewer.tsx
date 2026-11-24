export default function EvidenceViewer({ evidence }: { evidence: string }) {
  return (
    <div className="card">
      <div style={{ fontSize: '0.85rem', color: '#b8afc5', marginBottom: 4 }}>
        Evidence
      </div>
      <div style={{ whiteSpace: 'pre-wrap' }}>{evidence || '—'}</div>
    </div>
  );
}
