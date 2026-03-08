from fastapi import APIRouter
from mock_data import ENTITY_MISSES, EVALUATION_RUNS
from models import EntityMiss, EvaluationRun

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


@router.get("/runs", response_model=list[EvaluationRun])
async def get_evaluation_runs():
    return EVALUATION_RUNS


@router.get("/latest", response_model=EvaluationRun)
async def get_latest_run():
    return EVALUATION_RUNS[-1]


@router.get("/misses", response_model=list[EntityMiss])
async def get_entity_misses(
    miss_type: str | None = None,
    entity_type: str | None = None,
    risk_level: str | None = None,
):
    """Return entity misses with optional filtering."""
    results = ENTITY_MISSES
    if miss_type and miss_type != "all":
        results = [m for m in results if m.miss_type == miss_type]
    if entity_type and entity_type != "all":
        results = [m for m in results if m.entity_type == entity_type]
    if risk_level and risk_level != "all":
        results = [m for m in results if m.risk_level == risk_level]
    return results


@router.get("/metrics")
async def get_metrics():
    """Return overall and per-entity-type metrics for the latest run."""
    latest = EVALUATION_RUNS[-1]
    return {
        "overall": {
            "precision": 94,
            "recall": 88,
            "f1_score": 91,
            "false_negatives": 40,
        },
        "by_entity_type": [
            {"type": "PERSON", "precision": 96, "recall": 92, "f1": 94},
            {"type": "EMAIL", "precision": 98, "recall": 95, "f1": 96},
            {"type": "PHONE", "precision": 93, "recall": 89, "f1": 91},
            {"type": "SSN", "precision": 97, "recall": 84, "f1": 90},
            {"type": "CREDIT_CARD", "precision": 71, "recall": 65, "f1": 68},
            {"type": "MEDICAL_RECORD", "precision": 89, "recall": 81, "f1": 85},
        ],
        "errors": {
            "false_negatives": {
                "total": 40,
                "by_type": [
                    {"type": "CREDIT_CARD", "count": 12},
                    {"type": "MEDICAL_CONDITION", "count": 9},
                    {"type": "SSN", "count": 8},
                    {"type": "Other", "count": 11},
                ],
            },
            "false_positives": {
                "total": 19,
                "by_type": [
                    {"type": "DATE", "count": 7},
                    {"type": "PERSON", "count": 5},
                    {"type": "PHONE_NUMBER", "count": 4},
                    {"type": "Other", "count": 3},
                ],
            },
        },
        "run": latest.model_dump(),
    }


@router.get("/patterns")
async def get_error_patterns():
    return {
        "frequent_misses": [
            {
                "type": "CREDIT_CARD",
                "count": 12,
                "pattern": "Partial card numbers, low confidence scores",
            },
            {
                "type": "MEDICAL_CONDITION",
                "count": 9,
                "pattern": "Medical terminology not in baseline recognizers",
            },
            {
                "type": "SSN",
                "count": 8,
                "pattern": "Non-standard formatting (spaces instead of dashes)",
            },
            {
                "type": "INSURANCE_POLICY",
                "count": 6,
                "pattern": "Custom format not covered by patterns",
            },
        ],
        "common_patterns": [
            {
                "name": "Low Confidence Threshold",
                "description": (
                    "Credit card patterns are being detected but filtered out "
                    "due to confidence scores below threshold (typically 0.65-0.75)"
                ),
            },
            {
                "name": "Format Variations",
                "description": (
                    "SSN and phone numbers with non-standard separators "
                    "(spaces, periods) are being missed"
                ),
            },
            {
                "name": "Domain-Specific Terms",
                "description": (
                    "Medical conditions and insurance policy numbers "
                    "require custom recognizers for your domain"
                ),
            },
        ],
        "insights": [
            {
                "title": "Adjust Confidence Thresholds",
                "description": (
                    "Consider lowering the confidence threshold for CREDIT_CARD "
                    "entities from 0.70 to 0.60. This would capture 12 additional "
                    "credit card numbers that are currently being missed."
                ),
            },
            {
                "title": "Add Custom Recognizers",
                "description": (
                    "Create domain-specific recognizers for MEDICAL_CONDITION "
                    "(9 misses) and INSURANCE_POLICY (6 misses) to better handle "
                    "your healthcare dataset."
                ),
            },
            {
                "title": "Expand Pattern Variations",
                "description": (
                    "Update SSN and PHONE_NUMBER patterns to handle "
                    "alternative separators (spaces, periods, no "
                    "separators). This addresses 8 SSN misses."
                ),
            },
            {
                "title": "Strong Areas",
                "description": (
                    "EMAIL (98% precision, 95% recall) and PERSON "
                    "(96% precision, 92% recall) recognizers are "
                    "performing well and don't require tuning."
                ),
            },
        ],
    }
