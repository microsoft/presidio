export type ComplianceFramework = 'hipaa' | 'gdpr' | 'ccpa' | 'general';
export type SelectedComplianceFrameworks = ComplianceFramework[];

export type DatasetType = 'customer' | 'internal';

export interface Dataset {
  id: string;
  name: string;
  type: DatasetType;
  recordCount: number;
  description: string;
}

export interface Entity {
  text: string;
  entity_type: string;
  start: number;
  end: number;
  score?: number;
}

export interface Record {
  id: string;
  text: string;
  presidioEntities: Entity[];
  llmEntities: Entity[];
  datasetEntities?: Entity[];
  goldenEntities?: Entity[];
}

export interface UploadedDataset {
  id: string;
  filename: string;
  name: string;
  description: string;
  path: string;
  format: 'csv' | 'json';
  record_count: number;
  has_entities: boolean;
  columns: string[];
  text_column: string;
  entities_column?: string | null;
}

export interface SetupConfig {
  datasetId: string;
  complianceFrameworks: ComplianceFramework[];
  cloudRestriction: 'allowed' | 'restricted';
  runPresidio: boolean;
  runLlm: boolean;
  hasDatasetEntities: boolean;
}

export interface EvaluationMetrics {
  precision: number;
  recall: number;
  f1Score: number;
  falsePositives: number;
  falseNegatives: number;
  truePositives: number;
  trueNegatives: number;
}

export interface EvaluationRun {
  id: string;
  timestamp: Date;
  sampleSize: number;
  metrics: EvaluationMetrics;
  configVersion: string;
}

export interface EntityMiss {
  recordId: string;
  recordText: string;
  missedEntity: Entity;
  missType: 'false-positive' | 'false-negative';
  entityType: string;
  riskLevel: 'high' | 'medium' | 'low';
}
