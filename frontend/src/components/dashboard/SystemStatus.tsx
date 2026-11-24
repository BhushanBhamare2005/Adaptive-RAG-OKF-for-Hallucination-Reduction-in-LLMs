import { useEffect, useState } from 'react';
import { getHealth } from '../../services/experimentService';
import { HealthStatus } from '../../types';

export default function SystemStatus() {
  const [status, setStatus] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth()
      .then((s) => setStatus(s))
      .catch(() => setError('Backend is unreachable'));
  }, []);

  const ok = status?.status === 'ok';
  return (
    <div className="card">
      <div style={{ fontSize: '0.85rem', color: '#b8afc5' }}>Backend Status</div>
      <div style={{ color: ok ? '#00e5a0' : '#d946ef', fontWeight: 600 }}>
        {error ?? status?.status ?? 'Checking…'}
      </div>
      {status?.python && (
        <div style={{ fontSize: '0.75rem', color: '#81748f' }}>
          Python {status.python} · {status.platform}
        </div>
      )}
    </div>
  );
}
