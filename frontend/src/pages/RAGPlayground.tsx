import { useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import { ragQuery } from '../services/platformService';

export default function RAGPlayground() {
  const [question, setQuestion] = useState('');
  const [topK, setTopK] = useState(8);
  const [result, setResult] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function submit() {
    if (!question.trim()) { setError('Enter a question.'); return; }
    setBusy(true); setError('');
    try { setResult(await ragQuery({ question: question.trim(), top_k: topK, abstention_mode: true })); }
    catch (e: any) {
      const detail = e?.response?.data?.detail;
      if (typeof detail === 'string') setError(detail);
      else if (Array.isArray(detail)) setError(detail.map((item: any) => item.msg || item.message).filter(Boolean).join('; ') || 'RAG request failed.');
      else setError(detail?.message || e?.message || 'RAG request failed.');
    }
    finally { setBusy(false); }
  }
  return <div>
    <PageHeader eyebrow="Retrieval augmented generation" title="AI Chat / RAG Playground" description="Ask a question against the indexed knowledge base." />
    {error && <div className="alert error">{error}</div>}
    <div className="chat-layout">
      <section className="panel chat-panel">
        <div className="chat-history">
          {result ? <><div className="message user">{question}</div><div className={`message assistant ${result.abstained ? 'abstained' : ''}`}><strong>{result.abstained ? 'Answer withheld' : 'Verified response'}</strong><p>{result.answer || result.abstention_reason}</p></div></> : <div className="empty-state">Ask a question to retrieve and generate an answer.</div>}
        </div>
        <div className="composer"><textarea value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="What would you like to verify?" rows={3}/><div className="composer-actions"><label>Top-K <input className="number-input" type="number" min={1} max={50} value={topK} onChange={(e) => setTopK(Number(e.target.value))}/></label><button className="button primary" disabled={busy} onClick={submit}>{busy ? 'Retrieving...' : 'Send question'}</button></div></div>
      </section>
      <aside className="panel citations-panel"><div className="panel-header"><div><span className="eyebrow">Sources</span><h2>Citations</h2></div></div>
        {!result?.citations?.length ? <div className="empty-state">Retrieved sources will appear here.</div> : result.citations.map((item: any, index: number) => <article className="citation-card" key={item.chunk_id}><div className="citation-title"><span>{index + 1}</span><strong>{item.title}</strong></div><p>{item.excerpt}</p><small>Page {item.page_number || 'N/A'} · {(item.similarity_score * 100).toFixed(1)}% relevance</small></article>)}
      </aside>
    </div>
  </div>;
}
