from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""

    hipaa = "hipaa"
    gdpr = "gdpr"
    ccpa = "ccpa"
    general = "general"


class DatasetType(str, Enum):
    """Dataset origin type."""

    customer = "customer"
    internal = "internal"


class Dataset(BaseModel):
    """Dataset metadata."""

    id: str
    name: str
    type: DatasetType
    record_count: int
    description: str


class Entity(BaseModel):
    """A detected PII entity span."""

    text: str
    entity_type: str
    start: int
    end: int
    score: Optional[float] = None


class Record(BaseModel):
    """A text record with detected entities."""

    id: str
    text: str
    presidio_entities: list[Entity] = []
    llm_entities: list[Entity] = []
    dataset_entities: list[Entity] = []
    golden_entities: Optional[list[Entity]] = None
    final_entities: Optional[list[Entity]] = None


class EvaluationMetrics(BaseModel):
    """Precision/recall metrics for an evaluation run."""

    precision: float
    recall: float
    f1_score: float
    false_positives: int
    false_negatives: int
    true_positives: int
    true_negatives: int


class EvaluationRun(BaseModel):
    """Snapshot of a single evaluation run."""

    id: str
    timestamp: datetime
    sample_size: int
    metrics: EvaluationMetrics
    config_version: str


class MissType(str, Enum):
    """Classification of an entity miss."""

    false_positive = "false-positive"
    false_negative = "false-negative"


class RiskLevel(str, Enum):
    """Risk severity level."""

    high = "high"
    medium = "medium"
    low = "low"


class EntityMiss(BaseModel):
    """An entity detection miss (false positive or negative)."""

    record_id: str
    record_text: str
    missed_entity: Entity
    miss_type: MissType
    entity_type: str
    risk_level: RiskLevel


# --- Request / Response models ---


class DatasetLoadRequest(BaseModel):
    """Request to load a dataset from a file path."""

    path: str
    format: str  # "csv" | "json"
    text_column: str = "text"
    entities_column: str | None = None
    name: str | None = None  # user-friendly display name
    description: str | None = None  # optional description


class UploadedDataset(BaseModel):
    """Metadata for an uploaded dataset."""

    id: str
    filename: str
    name: str  # user-friendly display name
    description: str = ""  # optional user-provided description
    path: str  # absolute file path
    stored_path: str = ""  # local copy in backend/data/
    format: str  # "csv" | "json"
    record_count: int
    has_entities: bool
    has_final_entities: bool = False
    columns: list[str]
    text_column: str = "text"
    entities_column: str | None = None


class DatasetRenameRequest(BaseModel):
    """Request to rename a saved dataset."""

    name: str


class SetupConfig(BaseModel):
    """Initial evaluation setup configuration."""

    dataset_id: str
    compliance_frameworks: list[ComplianceFramework]
    cloud_restriction: str  # "allowed" | "restricted"
    run_presidio: bool = True
    run_llm: bool = True


class SamplingMethod(str, Enum):
    """Available sampling strategies."""

    random = "random"
    length = "length"


class SamplingConfig(BaseModel):
    """Sampling configuration parameters."""

    dataset_id: str
    sample_size: int = 500
    method: SamplingMethod = SamplingMethod.random


class AnalysisStatus(BaseModel):
    """Current progress of PII analysis."""

    presidio_progress: int
    llm_progress: int
    presidio_complete: bool
    llm_complete: bool
    presidio_stats: Optional[dict] = None
    llm_stats: Optional[dict] = None
    comparison: Optional[dict] = None


class EntityAction(BaseModel):
    """An entity review action (confirm/reject/add)."""

    entity: Entity
    source: str  # "presidio" | "llm" | "manual"


class DecisionType(str, Enum):
    """Final evaluation decision."""

    approve = "approve"
    iterate = "iterate"


class DecisionRequest(BaseModel):
    """Request to approve or iterate on the evaluation."""

    decision: DecisionType
    notes: str = ""
    selected_improvements: list[str] = []


class LLMConfig(BaseModel):
    """LLM Judge configuration — only deployment is chosen in the UI."""

    deployment_name: str = "gpt-4o"


class LLMAnalyzeRequest(BaseModel):
    """Request body for starting LLM analysis."""

    dataset_id: str
