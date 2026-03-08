from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ComplianceFramework(str, Enum):
    hipaa = "hipaa"
    gdpr = "gdpr"
    ccpa = "ccpa"
    general = "general"


class DatasetType(str, Enum):
    customer = "customer"
    internal = "internal"


class Dataset(BaseModel):
    id: str
    name: str
    type: DatasetType
    record_count: int
    description: str


class Entity(BaseModel):
    text: str
    entity_type: str
    start: int
    end: int
    score: Optional[float] = None


class Record(BaseModel):
    id: str
    text: str
    presidio_entities: list[Entity] = []
    llm_entities: list[Entity] = []
    dataset_entities: list[Entity] = []
    golden_entities: Optional[list[Entity]] = None


class EvaluationMetrics(BaseModel):
    precision: float
    recall: float
    f1_score: float
    false_positives: int
    false_negatives: int
    true_positives: int
    true_negatives: int


class EvaluationRun(BaseModel):
    id: str
    timestamp: datetime
    sample_size: int
    metrics: EvaluationMetrics
    config_version: str


class MissType(str, Enum):
    false_positive = "false-positive"
    false_negative = "false-negative"


class RiskLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class EntityMiss(BaseModel):
    record_id: str
    record_text: str
    missed_entity: Entity
    miss_type: MissType
    entity_type: str
    risk_level: RiskLevel


# --- Request / Response models ---


class DatasetLoadRequest(BaseModel):
    path: str
    format: str  # "csv" | "json"
    text_column: str = "text"
    entities_column: str | None = None


class UploadedDataset(BaseModel):
    id: str
    filename: str
    format: str  # "csv" | "json"
    record_count: int
    has_entities: bool
    columns: list[str]


class SetupConfig(BaseModel):
    dataset_id: str
    compliance_frameworks: list[ComplianceFramework]
    cloud_restriction: str  # "allowed" | "restricted"
    run_presidio: bool = True
    run_llm: bool = True


class SamplingConfig(BaseModel):
    dataset_id: str
    sample_size: int = 500


class AnalysisStatus(BaseModel):
    presidio_progress: int
    llm_progress: int
    presidio_complete: bool
    llm_complete: bool
    presidio_stats: Optional[dict] = None
    llm_stats: Optional[dict] = None
    comparison: Optional[dict] = None


class EntityAction(BaseModel):
    entity: Entity
    source: str  # "presidio" | "llm" | "manual"


class DecisionType(str, Enum):
    approve = "approve"
    iterate = "iterate"


class DecisionRequest(BaseModel):
    decision: DecisionType
    notes: str = ""
    selected_improvements: list[str] = []
