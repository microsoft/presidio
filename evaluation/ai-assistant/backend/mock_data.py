"""Mock data mirroring the frontend for demo / development purposes."""

from datetime import datetime

from models import (
    Dataset,
    DatasetType,
    Entity,
    EntityMiss,
    EvaluationMetrics,
    EvaluationRun,
    MissType,
    Record,
    RiskLevel,
)

DATASETS: list[Dataset] = [
    Dataset(
        id="ds-001",
        name="Patient Records 2025",
        type=DatasetType.customer,
        record_count=15000,
        description="Electronic health records from Q4 2025",
    ),
    Dataset(
        id="ds-002",
        name="Customer Support Tickets",
        type=DatasetType.customer,
        record_count=8500,
        description="Support conversations with PII",
    ),
    Dataset(
        id="ds-003",
        name="Internal HR Data",
        type=DatasetType.internal,
        record_count=2300,
        description="Employee records and performance reviews",
    ),
    Dataset(
        id="ds-004",
        name="Financial Transaction Logs",
        type=DatasetType.customer,
        record_count=42000,
        description="Payment and billing information",
    ),
]

RECORDS: list[Record] = [
    Record(
        id="rec-001",
        text=(
            "Patient John Smith, DOB 03/15/1985, was admitted on 2025-01-10. "
            "Contact: john.smith@email.com, Phone: 555-0123. SSN: 123-45-6789."
        ),
        presidio_entities=[
            Entity(text="John Smith", type="PERSON", start=8, end=18, score=0.95),
            Entity(text="03/15/1985", type="DATE_OF_BIRTH", start=24, end=34, score=0.92),
            Entity(text="john.smith@email.com", type="EMAIL", start=77, end=97, score=0.98),
            Entity(text="555-0123", type="PHONE_NUMBER", start=106, end=114, score=0.89),
            Entity(text="123-45-6789", type="US_SSN", start=121, end=132, score=0.99),
        ],
        llm_entities=[
            Entity(text="John Smith", type="PERSON", start=8, end=18, score=0.96),
            Entity(text="03/15/1985", type="DATE_OF_BIRTH", start=24, end=34, score=0.94),
            Entity(text="2025-01-10", type="DATE", start=52, end=62, score=0.88),
            Entity(text="john.smith@email.com", type="EMAIL", start=77, end=97, score=0.97),
            Entity(text="555-0123", type="PHONE_NUMBER", start=106, end=114, score=0.91),
            Entity(text="123-45-6789", type="US_SSN", start=121, end=132, score=0.98),
        ],
    ),
    Record(
        id="rec-002",
        text="Dr. Sarah Johnson reviewed the case. Medical Record #MR-445521. Insurance Policy: POL-8821-USA.",
        presidio_entities=[
            Entity(text="Sarah Johnson", type="PERSON", start=4, end=17, score=0.93),
            Entity(text="MR-445521", type="MEDICAL_RECORD", start=55, end=64, score=0.87),
        ],
        llm_entities=[
            Entity(text="Dr. Sarah Johnson", type="PERSON", start=0, end=17, score=0.95),
            Entity(text="MR-445521", type="MEDICAL_RECORD", start=55, end=64, score=0.89),
            Entity(text="POL-8821-USA", type="INSURANCE_POLICY", start=84, end=96, score=0.82),
        ],
    ),
    Record(
        id="rec-003",
        text=(
            "Employee ID: EMP-8821, Jane Doe, started 2023-06-01. "
            "Salary: $85,000. Emergency contact: Mike Doe at 555-9876."
        ),
        presidio_entities=[
            Entity(text="EMP-8821", type="EMPLOYEE_ID", start=13, end=21, score=0.91),
            Entity(text="Jane Doe", type="PERSON", start=23, end=31, score=0.94),
            Entity(text="2023-06-01", type="DATE", start=41, end=51, score=0.96),
            Entity(text="Mike Doe", type="PERSON", start=89, end=97, score=0.92),
            Entity(text="555-9876", type="PHONE_NUMBER", start=101, end=109, score=0.88),
        ],
        llm_entities=[
            Entity(text="EMP-8821", type="EMPLOYEE_ID", start=13, end=21, score=0.90),
            Entity(text="Jane Doe", type="PERSON", start=23, end=31, score=0.96),
            Entity(text="2023-06-01", type="DATE", start=41, end=51, score=0.94),
            Entity(text="$85,000", type="SALARY", start=61, end=68, score=0.79),
            Entity(text="Mike Doe", type="PERSON", start=89, end=97, score=0.93),
            Entity(text="555-9876", type="PHONE_NUMBER", start=101, end=109, score=0.90),
        ],
    ),
    Record(
        id="rec-004",
        text=(
            "Credit card ending in 4532 was used for transaction. "
            "Customer: alice.wong@company.com. IP: 192.168.1.100"
        ),
        presidio_entities=[
            Entity(text="4532", type="CREDIT_CARD", start=22, end=26, score=0.65),
            Entity(text="alice.wong@company.com", type="EMAIL", start=64, end=86, score=0.97),
            Entity(text="192.168.1.100", type="IP_ADDRESS", start=92, end=105, score=0.99),
        ],
        llm_entities=[
            Entity(text="alice.wong@company.com", type="EMAIL", start=64, end=86, score=0.98),
            Entity(text="192.168.1.100", type="IP_ADDRESS", start=92, end=105, score=0.97),
        ],
    ),
    Record(
        id="rec-005",
        text=(
            "Prescription for Robert Chen: Medication ABC-123, dosage 50mg. "
            "Doctor notes indicate history of diabetes."
        ),
        presidio_entities=[
            Entity(text="Robert Chen", type="PERSON", start=17, end=28, score=0.94),
            Entity(text="ABC-123", type="MEDICATION_CODE", start=41, end=48, score=0.71),
        ],
        llm_entities=[
            Entity(text="Robert Chen", type="PERSON", start=17, end=28, score=0.95),
            Entity(text="ABC-123", type="MEDICATION_CODE", start=41, end=48, score=0.73),
            Entity(text="diabetes", type="MEDICAL_CONDITION", start=97, end=105, score=0.86),
        ],
    ),
]

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
        record_text="Credit card ending in 4532 was used for transaction. Customer: alice.wong@company.com.",
        missed_entity=Entity(text="4532", type="CREDIT_CARD", start=22, end=26, score=0.65),
        miss_type=MissType.false_negative,
        entity_type="CREDIT_CARD",
        risk_level=RiskLevel.high,
    ),
    EntityMiss(
        record_id="rec-002",
        record_text="Dr. Sarah Johnson reviewed the case. Insurance Policy: POL-8821-USA.",
        missed_entity=Entity(text="POL-8821-USA", type="INSURANCE_POLICY", start=56, end=68),
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
        missed_entity=Entity(text="diabetes", type="MEDICAL_CONDITION", start=97, end=105),
        miss_type=MissType.false_negative,
        entity_type="MEDICAL_CONDITION",
        risk_level=RiskLevel.high,
    ),
    EntityMiss(
        record_id="rec-003",
        record_text="Employee ID: EMP-8821, Jane Doe, started 2023-06-01. Salary: $85,000.",
        missed_entity=Entity(text="$85,000", type="SALARY", start=61, end=68),
        miss_type=MissType.false_negative,
        entity_type="SALARY",
        risk_level=RiskLevel.medium,
    ),
]
