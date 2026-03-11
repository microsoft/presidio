import csv
import json
import os
from collections import Counter

from fastapi import APIRouter, HTTPException, Query
from mock_data import ENTITY_MISSES, EVALUATION_RUNS
from models import Entity, EntityMiss, EvaluationRun, MissType, RiskLevel
from routers.upload import _resolve_path, _uploaded

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


def _parse_entities(raw: str | list | None) -> list[Entity]:
    if not raw:
        return []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return []
    if not isinstance(raw, list):
        return []
    entities: list[Entity] = []
    for item in raw:
        if isinstance(item, dict):
            try:
                entities.append(Entity(**item))
            except Exception:
                continue
    return entities


def _entity_key(entity: Entity) -> tuple[str, int, int, str]:
    return (entity.entity_type, entity.start, entity.end, entity.text)


def _risk_level(entity_type: str) -> RiskLevel:
    high = {
        "CREDIT_CARD",
        "CRYPTO",
        "IBAN_CODE",
        "MEDICAL_RECORD",
        "PASSPORT",
        "SSN",
        "US_BANK_NUMBER",
        "US_DRIVER_LICENSE",
        "US_ITIN",
        "US_PASSPORT",
        "US_SSN",
    }
    medium = {
        "DATE_TIME",
        "EMAIL_ADDRESS",
        "LOCATION",
        "ORGANIZATION",
        "PERSON",
        "PHONE_NUMBER",
        "URL",
    }
    if entity_type in high:
        return RiskLevel.high
    if entity_type in medium:
        return RiskLevel.medium
    return RiskLevel.low


def _pct(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 1)


def _evaluate_config(rows: list[dict], text_column: str, config_name: str) -> dict:
    misses: list[dict] = []
    per_type = Counter()
    predicted_per_type = Counter()
    tp_per_type = Counter()
    tp_total = 0
    fp_total = 0
    fn_total = 0

    for index, row in enumerate(rows):
        record_id = f"rec-{index + 1:04d}"
        record_text = (row.get(text_column) or "").strip()
        gold_entities = _parse_entities(row.get("final_entities"))
        predicted_entities = _parse_entities(row.get(f"config_{config_name}"))

        gold_map = {_entity_key(entity): entity for entity in gold_entities}
        predicted_map = {_entity_key(entity): entity for entity in predicted_entities}

        for entity in gold_map.values():
            per_type[entity.entity_type] += 1
        for entity in predicted_map.values():
            predicted_per_type[entity.entity_type] += 1

        for key, entity in predicted_map.items():
            if key in gold_map:
                tp_total += 1
                tp_per_type[entity.entity_type] += 1
            else:
                fp_total += 1
                misses.append(
                    EntityMiss(
                        record_id=record_id,
                        record_text=record_text,
                        missed_entity=entity,
                        miss_type=MissType.false_positive,
                        entity_type=entity.entity_type,
                        risk_level=_risk_level(entity.entity_type),
                    ).model_dump()
                )

        for key, entity in gold_map.items():
            if key not in predicted_map:
                fn_total += 1
                misses.append(
                    EntityMiss(
                        record_id=record_id,
                        record_text=record_text,
                        missed_entity=entity,
                        miss_type=MissType.false_negative,
                        entity_type=entity.entity_type,
                        risk_level=_risk_level(entity.entity_type),
                    ).model_dump()
                )

    entity_types = sorted(set(per_type.keys()) | set(predicted_per_type.keys()))
    by_entity_type = []
    for entity_type in entity_types:
        tp = tp_per_type[entity_type]
        pred = predicted_per_type[entity_type]
        gold = per_type[entity_type]
        precision = _pct(tp, pred)
        recall = _pct(tp, gold)
        f1 = round((2 * precision * recall / (precision + recall)), 1) if precision + recall else 0.0
        by_entity_type.append({
            "type": entity_type,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        })

    overall_precision = _pct(tp_total, tp_total + fp_total)
    overall_recall = _pct(tp_total, tp_total + fn_total)
    overall_f1 = round((2 * overall_precision * overall_recall / (overall_precision + overall_recall)), 1) if overall_precision + overall_recall else 0.0
    risk_counts = Counter(miss["risk_level"] for miss in misses)

    return {
        "config_name": config_name,
        "overall": {
            "precision": overall_precision,
            "recall": overall_recall,
            "f1_score": overall_f1,
            "true_positives": tp_total,
            "false_positives": fp_total,
            "false_negatives": fn_total,
        },
        "by_entity_type": by_entity_type,
        "misses": misses,
        "summary": {
            "total_misses": len(misses),
            "false_positives": fp_total,
            "false_negatives": fn_total,
            "high_risk": risk_counts[RiskLevel.high],
            "medium_risk": risk_counts[RiskLevel.medium],
            "low_risk": risk_counts[RiskLevel.low],
        },
    }


@router.get("/summary")
async def get_evaluation_summary(
    dataset_id: str,
    config_names: list[str] | None = Query(default=None),
):
    ds = _uploaded.get(dataset_id)
    if ds is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    resolved = ds.stored_path if ds.stored_path and os.path.isfile(ds.stored_path) else _resolve_path(ds.path)
    if not os.path.isfile(resolved):
        raise HTTPException(status_code=404, detail="Dataset file not found on disk")

    if ds.format != "csv":
        raise HTTPException(status_code=400, detail="Only CSV evaluation is currently supported")

    with open(resolved, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    available_configs = list(ds.ran_configs or [])
    if not available_configs and rows:
        available_configs = [
            key.replace("config_", "")
            for key in rows[0].keys()
            if key.startswith("config_")
        ]

    default_config = available_configs[-1] if available_configs else None
    selected_configs = [c for c in (config_names or ([default_config] if default_config else [])) if c in available_configs]

    has_final_entities = False

    for row in rows:
        gold_entities = _parse_entities(row.get("final_entities"))
        if gold_entities:
            has_final_entities = True

    if not has_final_entities:
        raise HTTPException(status_code=400, detail="No reviewed final entities found for this dataset")

    per_config = [_evaluate_config(rows, ds.text_column, config_name) for config_name in selected_configs]

    return {
        "dataset_id": dataset_id,
        "available_configs": available_configs,
        "selected_configs": selected_configs,
        "default_config": default_config,
        "per_config": per_config,
    }


@router.get("/runs", response_model=list[EvaluationRun])
async def get_evaluation_runs():
    """List all evaluation runs."""
    return EVALUATION_RUNS


@router.get("/latest", response_model=EvaluationRun)
async def get_latest_run():
    """Return the most recent evaluation run."""
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
    """Return common error patterns and insights."""
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
