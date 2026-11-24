import { useEffect, useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import { getDocuments, deleteDocument, reindexDocument } from '../services/platformService';

export default function KnowledgeBase() {
  const [docs, setDocs] = useState<any[]>([]);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState('');
  async function load() {
    try { setDocs((await getDocuments()).documents || []); } catch (e: any) { setError(e?.response?.data?.detail || 'Could not load documents.'); }
  }
  useEffect(() => { load(); }, []);
  async function remove(id: string) {
    if (!window.confirm('Delete this document and its chunks?')) return;
    setBusy(id); await deleteDocument(id).catch((e) => setError(e?.response?.data?.detail || 'Delete failed.'));
    await load(); setBusy('');
  }
  async function reindex(id: string) {
    setBusy(id); await reindexDocument(id).catch((e) => setError(e?.response?.data?.detail || 'Re-index failed.'));
    await load(); setBusy('');
  }
  return <div>
    <PageHeader eyebrow="Knowledge operations" title="AI Knowledge Base" description="Manage uploaded and web-source documents, versions and indexing status." action={<a className="button primary" href="/upload">Add documents</a>} />
    {error && <div className="alert error">{error}</div>}
    <section className="panel">
      {docs.length === 0 ? <div className="empty-state">No documents indexed. Upload a document or ingest a website.</div> :
      <div className="table-wrap"><table><thead><tr><th>Document</th><th>Source</th><th>Status</th><th>Version</th><th>Actions</th></tr></thead><tbody>
        {docs.map((doc) => <tr key={doc.id}><td><strong>{doc.title}</strong><small className="cell-subtitle">{doc.original_filename}</small></td><td>{doc.source_type}</td><td><span className={`badge ${doc.status}`}>{doc.status}</span></td><td>v{doc.version}</td><td><div className="row-actions"><button className="button secondary" disabled={busy === doc.id} onClick={() => reindex(doc.id)}>Re-index</button><button className="button danger" disabled={busy === doc.id} onClick={() => remove(doc.id)}>Delete</button></div></td></tr>)}
      </tbody></table></div>}
    </section>
  </div>;
}
