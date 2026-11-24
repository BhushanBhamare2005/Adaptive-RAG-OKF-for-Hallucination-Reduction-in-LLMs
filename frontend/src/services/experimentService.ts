import { api } from './api';
import {
  ComparisonMap,
  DataRecord,
  DatasetSummary,
  HealthStatus,
  TrainingResponse,
} from '../types';

export async function getComparison(): Promise<ComparisonMap> {
  const { data } = await api.get<ComparisonMap>('/experiments/comparison');
  return data;
}

export async function getHealth(): Promise<HealthStatus> {
  const { data } = await api.get<HealthStatus>('/health');
  return data;
}

export async function getDatasetSummary(): Promise<DatasetSummary> {
  const { data } = await api.get<DatasetSummary>('/datasets/');
  return data;
}

export async function getDatasetSample(n = 5): Promise<DataRecord[]> {
  const { data } = await api.get<DataRecord[]>('/datasets/sample', { params: { n } });
  return data;
}

export async function trainModels(): Promise<TrainingResponse> {
  const { data } = await api.post<TrainingResponse>('/experiments/train');
  return data;
}
