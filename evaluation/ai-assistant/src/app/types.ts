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
  type: string;
  start: number;
  end: number;
  score?: number;
}

export interface Record {
  id: string;
  text: string;
  presidioEntities: Entity[];
  llmEntities: Entity[];
  goldenEntities?: Entity[];
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
