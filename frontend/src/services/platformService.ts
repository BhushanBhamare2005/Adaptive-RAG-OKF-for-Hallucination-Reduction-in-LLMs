import { api } from './api';

export async function getOverview() {
  const { data } = await api.get('/dashboard/overview');
  return data;
}

export async function getDocuments() {
  const { data } = await api.get('/documents');
  return data;
}

export async function uploadDocument(file: File) {
  const form = new FormData();
  form.append('file', file);
  const { data } = await api.post('/documents/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function ingestUrl(url: string, title = '') {
  const { data } = await api.post('/documents/url', { url, title });
  return data;
}

export async function deleteDocument(id: string) {
  const { data } = await api.delete(`/documents/${id}`);
  return data;
}

export async function reindexDocument(id: string) {
  const { data } = await api.post(`/documents/${id}/reindex`);
  return data;
}

export async function ragQuery(payload: {
  question: string;
  model_name?: string;
  top_k?: number;
  abstention_mode?: boolean;
}) {
  const { data } = await api.post('/rag/query', payload);
  return data;
}

export async function searchEvidence(question: string, top_k = 8) {
  const { data } = await api.post('/rag/search', { question, top_k });
  return data;
}

export async function verifyAnswer(answer: string, query_id?: string) {
  const { data } = await api.post('/verification/answer', { answer, query_id });
  return data;
}

export async function runAEVL(answer: string, question: string) {
  const { data } = await api.post('/aevl/run', { answer, question });
  return data;
}

export async function getAEVLRuns() {
  const { data } = await api.get('/aevl/runs');
  return data;
}

export async function getConflicts() {
  const { data } = await api.get('/conflicts');
  return data;
}

export async function detectConflicts() {
  const { data } = await api.post('/conflicts/detect');
  return data;
}

export async function resolveConflict(id: string, payload: { resolution_status: string; resolved_by: string; resolution_notes: string }) {
  const { data } = await api.put(`/conflicts/${id}/resolve`, payload);
  return data;
}

export async function getAdaptiveConfig() {
  const { data } = await api.get('/adaptive-okf/config');
  return data;
}

export async function evaluateAdaptive(payload: {
  model: string;
  answer: string;
  evidence: string;
  question?: string;
}) {
  const { data } = await api.post('/adaptive-okf/evaluate', payload);
  return data;
}

export async function getExplainModels() {
  const { data } = await api.get('/explainability/models');
  return data;
}

export async function explainPrediction(modelName: string, answer: string, evidence: string) {
  const { data } = await api.post(`/explainability/models/${modelName}/prediction`, null, {
    params: { answer, evidence },
  });
  return data;
}

export async function getAuditEvents() {
  const { data } = await api.get('/audit/events');
  return data;
}

export async function getRiskSettings() {
  const { data } = await api.get('/settings/risk');
  return data;
}

export async function updateRiskSettings(payload: {
  abstention_risk_threshold: number;
  supported_claim_threshold: number;
  contradiction_threshold: number;
  aevl_max_loops: number;
}) {
  const { data } = await api.put('/settings/risk', payload);
  return data;
}

export async function getProviderConfig() {
  const { data } = await api.get('/settings/providers/config');
  return data;
}

export async function getProviderStatus() {
  const { data } = await api.get('/settings/providers');
  return data;
}

export async function updateProviderConfig(payload: {
  provider: 'openai_compatible' | 'ollama';
  base_url: string;
  api_key: string;
  model: string;
}) {
  const { data } = await api.put('/settings/providers', payload);
  return data;
}

export async function testProviderConfig(payload: {
  provider: 'openai_compatible' | 'ollama';
  base_url: string;
  api_key: string;
  model: string;
}) {
  const { data } = await api.post('/settings/providers/test', payload);
  return data;
}

export async function submitFeedback(payload: {
  query_id: string;
  action: 'approved' | 'rejected' | 'edited';
  corrected_answer?: string;
  comment?: string;
}) {
  const { data } = await api.post('/feedback', payload);
  return data;
}
