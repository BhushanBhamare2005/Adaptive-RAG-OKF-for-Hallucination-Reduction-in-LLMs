export interface FeatureContribution {
  name: string;
  value: number;
}

export interface AnalyzeResponse {
  model: string;
  risk_score: number;
  hallucinated: boolean;
  features: FeatureContribution[];
  message: string;
}

export interface AnalyzeRequest {
  model: string;
  question?: string;
  answer: string;
  evidence: string;
}

export interface DatasetSummary {
  total: number;
  sources: Record<string, number>;
}

export interface HealthStatus {
  status: string;
  python: string;
  platform: string;
  models_dir: string;
}

export interface DataRecord {
  question: string;
  answer: string;
  evidence: string;
  label: number;
  source?: string;
}

export interface ModelMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  roc_auc: number | null;
}

export type ComparisonMap = Record<string, ModelMetrics>;

export interface TrainingResponse {
  status: string;
  comparison: ComparisonMap;
}
