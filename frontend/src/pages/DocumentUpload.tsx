import { useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import { uploadDocument, ingestUrl } from '../services/platformService';

export default function DocumentUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState('');
  const [title, setTitle] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  async function upload() {
    if (!file) { setError('Choose a PDF, DOCX, TXT, MD or CSV file.'); return; }
    setBusy(true); setError(''); setMessage('');
    try { const result = await uploadDocument(file); setMessage(result.duplicate ? 'The document already exists in the knowledge base.' : 'Document uploaded and queued for indexing.'); }
    catch (e: any) { setError(e?.response?.data?.detail || 'Upload failed.'); }
    finally { setBusy(false); }
  }
  async function ingest() {
    if (!url.trim()) { setError('Enter a website URL.'); return; }
    const enteredUrl = url.trim();
    const normalizedUrl = /^https?:\/\//i.test(enteredUrl) ? enteredUrl : `https://${enteredUrl}`;
    try {
      new URL(normalizedUrl);
    } catch {
      setError('Enter a valid website URL, such as https://example.com/article.');
      return;
    }
    setBusy(true); setError(''); setMessage('');
    try {
      const result = await ingestUrl(normalizedUrl, title.trim());
      if (result.status !== 'indexed') {
        setError(result.error_message || 'The website was fetched, but indexing failed.');
        return;
      }
      setMessage(result.duplicate ? 'This website content is already in the knowledge base.' : 'Website ingested and indexed.');
    }
    catch (e: unknown) {
      const error = e as { response?: { data?: { detail?: string } }; message?: string };
      setError(error.response?.data?.detail || error.message || 'Website ingestion failed.');
    }
    finally { setBusy(false); }
  }
  return <div>
    <PageHeader eyebrow="Source ingestion" title="Document Upload Center" description="Add files or web sources to the verified knowledge base." />
    {message && <div className="alert success">{message}</div>}
    {error && <div className="alert error">{error}</div>}
    <div className="form-grid">
      <section className="panel upload-panel">
        <div className="panel-header"><div><span className="eyebrow">Local document</span><h2>Upload file</h2></div></div>
        <label className="drop-zone" htmlFor="document-file"><strong>{file ? file.name : 'Choose a document'}</strong><small>PDF, DOCX, TXT, MD or CSV · 4 MB maximum on hosted deployment</small></label>
        <input id="document-file" className="visually-hidden" type="file" accept=".pdf,.docx,.txt,.md,.csv" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button className="button primary full" disabled={busy} onClick={upload}>{busy ? 'Processing...' : 'Upload and index'}</button>
      </section>
      <section className="panel">
        <div className="panel-header"><div><span className="eyebrow">Web source</span><h2>Ingest website</h2></div></div>
        <label className="field-label">Title<input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Optional source title"/></label>
        <label className="field-label">Website URL<input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://example.com/article"/></label>
        <button className="button primary full" disabled={busy} onClick={ingest}>{busy ? 'Ingesting...' : 'Ingest website'}</button>
      </section>
    </div>
  </div>;
}
