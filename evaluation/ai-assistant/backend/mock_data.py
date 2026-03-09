"""Mock data for evaluation / decision stages only."""

from datetime import datetime

from models import (
    Entity,
    EntityMiss,
    EvaluationMetrics,
    EvaluationRun,
    MissType,
    RiskLevel,
)

EVALUATION_RUNS: list[EvaluationRun] = [
    EvaluationRun(
        id="run-001",
        timestamp=datetime(2025, 2, 20, 10, 30),
        sample_size=500,
        config_version="baseline-v1.0",
        metrics=EvaluationMetrics(
            precision=0.87,
            recall=0.73,
            f1_score=0.79,
            true_positives=245,
            false_positives=36,
            false_negatives=91,
            true_negatives=128,
        ),
    ),
    EvaluationRun(
        id="run-002",
        timestamp=datetime(2025, 2, 22, 14, 15),
        sample_size=500,
        config_version="tuned-v1.1",
        metrics=EvaluationMetrics(
            precision=0.91,
            recall=0.81,
            f1_score=0.86,
            true_positives=272,
            false_positives=27,
            false_negatives=64,
            true_negatives=137,
        ),
    ),
    EvaluationRun(
        id="run-003",
        timestamp=datetime(2025, 2, 25, 9, 0),
        sample_size=500,
        config_version="tuned-v1.2",
        metrics=EvaluationMetrics(
            precision=0.94,
            recall=0.88,
            f1_score=0.91,
            true_positives=296,
            false_positives=19,
            false_negatives=40,
            true_negatives=145,
        ),
    ),
]

ENTITY_MISSES: list[EntityMiss] = [
    EntityMiss(
        record_id="rec-004",
        record_text=(
            "Credit card ending in 4532 was used for "
            "transaction. Customer: alice.wong@company.com."
        ),
        missed_entity=Entity(
            text="4532", entity_type="CREDIT_CARD", start=22, end=26, score=0.65
        ),
        miss_type=MissType.false_negative,
        entity_type="CREDIT_CARD",
        risk_level=RiskLevel.high,
    ),
    EntityMiss(
        record_id="rec-002",
        record_text=(
            "Dr. Sarah Johnson reviewed the case. "
            "Insurance Policy: POL-8821-USA."
        ),
        missed_entity=Entity(
            text="POL-8821-USA", entity_type="INSURANCE_POLICY", start=56, end=68
        ),
        miss_type=MissType.false_negative,
        entity_type="INSURANCE_POLICY",
        risk_level=RiskLevel.medium,
    ),
    EntityMiss(
        record_id="rec-005",
        record_text=(
            "Prescription for Robert Chen: Medication ABC-123, dosage 50mg. "
            "Doctor notes indicate history of diabetes."
        ),
        missed_entity=Entity(
            text="diabetes", entity_type="MEDICAL_CONDITION", start=97, end=105
        ),
        miss_type=MissType.false_negative,
        entity_type="MEDICAL_CONDITION",
        risk_level=RiskLevel.high,
    ),
    EntityMiss(
        record_id="rec-003",
        record_text=(
            "Employee ID: EMP-8821, Jane Doe, "
            "started 2023-06-01. Salary: $85,000."
        ),
        missed_entity=Entity(text="$85,000", entity_type="SALARY", start=61, end=68),
        miss_type=MissType.false_negative,
        entity_type="SALARY",
        risk_level=RiskLevel.medium,
    ),
]
