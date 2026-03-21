import { EvaluationRun, EntityMiss } from '../types';

export const mockEvaluationRuns: EvaluationRun[] = [
  {
    id: 'run-001',
    timestamp: new Date('2025-02-20T10:30:00'),
    sampleSize: 500,
    configVersion: 'baseline-v1.0',
    metrics: {
      precision: 0.87,
      recall: 0.73,
      f1Score: 0.79,
      truePositives: 245,
      falsePositives: 36,
      falseNegatives: 91,
      trueNegatives: 128,
    },
  },
  {
    id: 'run-002',
    timestamp: new Date('2025-02-22T14:15:00'),
    sampleSize: 500,
    configVersion: 'tuned-v1.1',
    metrics: {
      precision: 0.91,
      recall: 0.81,
      f1Score: 0.86,
      truePositives: 272,
      falsePositives: 27,
      falseNegatives: 64,
      trueNegatives: 137,
    },
  },
  {
    id: 'run-003',
    timestamp: new Date('2025-02-25T09:00:00'),
    sampleSize: 500,
    configVersion: 'tuned-v1.2',
    metrics: {
      precision: 0.94,
      recall: 0.88,
      f1Score: 0.91,
      truePositives: 296,
      falsePositives: 19,
      falseNegatives: 40,
      trueNegatives: 145,
    },
  },
];

export const mockEntityMisses: EntityMiss[] = [
  {
    recordId: 'rec-004',
    recordText: 'Credit card ending in 4532 was used for transaction. Customer: alice.wong@company.com.',
    missedEntity: { text: '4532', entity_type: 'CREDIT_CARD', start: 22, end: 26, score: 0.65 },
    missType: 'false-negative',
    entityType: 'CREDIT_CARD',
    riskLevel: 'high',
  },
  {
    recordId: 'rec-002',
    recordText: 'Dr. Sarah Johnson reviewed the case. Insurance Policy: POL-8821-USA.',
    missedEntity: { text: 'POL-8821-USA', entity_type: 'INSURANCE_POLICY', start: 56, end: 68 },
    missType: 'false-negative',
    entityType: 'INSURANCE_POLICY',
    riskLevel: 'medium',
  },
  {
    recordId: 'rec-005',
    recordText: 'Prescription for Robert Chen: Medication ABC-123, dosage 50mg. Doctor notes indicate history of diabetes.',
    missedEntity: { text: 'diabetes', entity_type: 'MEDICAL_CONDITION', start: 97, end: 105 },
    missType: 'false-negative',
    entityType: 'MEDICAL_CONDITION',
    riskLevel: 'high',
  },
  {
    recordId: 'rec-003',
    recordText: 'Employee ID: EMP-8821, Jane Doe, started 2023-06-01. Salary: $85,000.',
    missedEntity: { text: '$85,000', entity_type: 'SALARY', start: 61, end: 68 },
    missType: 'false-negative',
    entityType: 'SALARY',
    riskLevel: 'medium',
  },
];
