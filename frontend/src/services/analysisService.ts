import { api } from './api';
import { AnalyzeRequest, AnalyzeResponse } from '../types';

export async function analyzeAnswer(payload: AnalyzeRequest): Promise<AnalyzeResponse> {
  const { data } = await api.post<AnalyzeResponse>('/analysis', payload);
  return data;
}
