import { useEffect, useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import {
  getRiskSettings,
  updateRiskSettings,
  getProviderConfig,
  getProviderStatus,
  updateProviderConfig,
  testProviderConfig,
} from '../services/platformService';

export default function Settings() {
  const [settings, setSettings] = useState({ abstention_risk_threshold: 0.75, supported_claim_threshold: 0.70, contradiction_threshold: 0.70, aevl_max_loops: 3 });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [provider, setProvider] = useState<{
    provider: 'openai_compatible' | 'ollama';
    base_url: string;
    api_key: string;
    model: string;
  }>({
    provider: 'ollama',
    base_url: 'http://127.0.0.1:11434',
    api_key: '',
    model: '',
  });
  const [providerStatus, setProviderStatus] = useState<any>(null);
  useEffect(() => {
    getRiskSettings().then(setSettings).catch((e) => setError(e?.response?.data?.detail || 'Settings unavailable.'));
    getProviderConfig().then((data) => setProvider({
      provider: data.provider || 'ollama',
      base_url: data.base_url || 'http://127.0.0.1:11434',
      api_key: '',
      model: data.model || '',
    })).catch(() => undefined);
    getProviderStatus().then(setProviderStatus).catch(() => undefined);
  }, []);
  async function save() { setError(''); setMessage(''); try { await updateRiskSettings(settings); setMessage('Risk settings saved.'); } catch (e: any) { setError(e?.response?.data?.detail || 'Could not save settings.'); } }
  const setNumber = (key: keyof typeof settings, value: number) => setSettings((current) => ({ ...current, [key]: value }));
  async function saveProvider() {
    setError('');
    setMessage('');
    try {
      const result = await updateProviderConfig(provider);
      setMessage(result.configured ? 'LLM provider saved and ready.' : 'Provider settings saved; complete the required fields.');
      setProviderStatus(await getProviderStatus());
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Could not save provider settings.');
    }
  }
  async function testProvider() {
    setError('');
    setMessage('');
    try {
      const result = await testProviderConfig(provider);
      if (result.status === 'connected') setMessage(`Provider connected: ${result.model}`);
      else setError(result.message || 'Provider test failed.');
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Provider test failed.');
    }
  }
  return <div>
    <PageHeader eyebrow="Platform configuration" title="Settings and Model Configuration" description="Configure adaptive thresholds and verification loop limits." />
    {message && <div className="alert success">{message}</div>}{error && <div className="alert error">{error}</div>}
    <section className="panel settings-panel"><div className="panel-header"><div><span className="eyebrow">LLM provider</span><h2>Generation configuration</h2></div></div>
      <div className="provider-status">
        <span>Status</span>
        <strong className={providerStatus?.llm?.status === 'configured' ? 'success-text' : 'warning-text'}>
          {providerStatus?.llm?.status || 'checking'}
        </strong>
      </div>
      <label className="field-label">Provider
        <select value={provider.provider} onChange={(e) => setProvider((current) => ({
          ...current,
          provider: e.target.value as 'openai_compatible' | 'ollama',
          base_url: e.target.value === 'ollama'
            ? 'http://127.0.0.1:11434'
            : current.base_url,
        }))}>
          <option value="ollama">Ollama (local)</option>
          <option value="openai_compatible">OpenAI-compatible API</option>
        </select>
      </label>
      <label className="field-label">Base URL
        <input
          value={provider.base_url}
          onChange={(e) => setProvider((current) => ({ ...current, base_url: e.target.value }))}
          placeholder={provider.provider === 'ollama' ? 'http://127.0.0.1:11434' : 'https://api.openai.com/v1'}
        />
      </label>
      <label className="field-label">Model
        <input
          value={provider.model}
          onChange={(e) => setProvider((current) => ({ ...current, model: e.target.value }))}
          placeholder={provider.provider === 'ollama' ? 'llama3.1' : 'gpt-4o-mini'}
        />
      </label>
      {provider.provider === 'openai_compatible' && (
        <label className="field-label">API key
          <input
            type="password"
            value={provider.api_key}
            onChange={(e) => setProvider((current) => ({ ...current, api_key: e.target.value }))}
            placeholder="Stored server-side; never displayed"
          />
        </label>
      )}
      <div className="row-actions">
        <button className="button secondary" onClick={testProvider}>Test provider</button>
        <button className="button primary" onClick={saveProvider}>Save provider</button>
      </div>
    </section>
    <section className="panel settings-panel"><div className="panel-header"><div><span className="eyebrow">Risk policy</span><h2>Verification thresholds</h2></div></div>
      <label className="range-field"><span>Abstention risk threshold</span><strong>{settings.abstention_risk_threshold}</strong><input type="range" min="0" max="1" step="0.01" value={settings.abstention_risk_threshold} onChange={(e) => setNumber('abstention_risk_threshold', Number(e.target.value))}/></label>
      <label className="range-field"><span>Supported claim threshold</span><strong>{settings.supported_claim_threshold}</strong><input type="range" min="0" max="1" step="0.01" value={settings.supported_claim_threshold} onChange={(e) => setNumber('supported_claim_threshold', Number(e.target.value))}/></label>
      <label className="range-field"><span>Contradiction threshold</span><strong>{settings.contradiction_threshold}</strong><input type="range" min="0" max="1" step="0.01" value={settings.contradiction_threshold} onChange={(e) => setNumber('contradiction_threshold', Number(e.target.value))}/></label>
      <label className="field-label">Maximum AEVL loops<input type="number" min="1" max="10" value={settings.aevl_max_loops} onChange={(e) => setNumber('aevl_max_loops', Number(e.target.value))}/></label>
      <button className="button primary" onClick={save}>Save configuration</button>
    </section>
  </div>;
}
