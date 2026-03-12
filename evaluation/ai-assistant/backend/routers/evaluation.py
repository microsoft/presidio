from __future__ import annotations

import csv
import json
import logging
import os
from collections import Counter

from fastapi import APIRouter, HTTPException, Query
from models import Entity, EntityMiss, MissType, RiskLevel
from presidio_evaluator import InputSample, Span, span_to_tag
from presidio_evaluator.evaluation import EvaluationResult, SpanEvaluator

from routers.upload import _resolve_path, _uploaded

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])

logger = logging.getLogger(__name__)

def _parse_entities_raw(raw: str | list | None) -> list[dict]:
    """Parse entity column into a list of dicts."""
    if not raw:
        return []
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return []
    if isinstance(raw, list):
        return raw
    return []


def _risk_level(entity_type: str) -> RiskLevel:
    high = {
        "CREDIT_CARD", "CRYPTO", "IBAN_CODE", "MEDICAL_RECORD", "PASSPORT",
        "SSN", "US_BANK_NUMBER", "US_DRIVER_LICENSE", "US_ITIN", "US_PASSPORT",
        "US_SSN",
    }
    medium = {
        "DATE_TIME", "EMAIL_ADDRESS", "LOCATION", "ORGANIZATION", "PERSON",
        "PHONE_NUMBER", "URL",
    }
    if entity_type in high:
        return RiskLevel.high
    if entity_type in medium:
        return RiskLevel.medium
    return RiskLevel.low


def _evaluate_config(rows: list[dict], text_column: str, config_name: str) -> dict:
    """Evaluate a single config using presidio-evaluator's SpanEvaluator."""
    pred_column = f"config_{config_name}"

    # Build InputSamples and prediction tags
    dataset: list[InputSample] = []
    all_predictions: list[list[str]] = []
    row_indices: list[int] = []

    for idx, row in enumerate(rows):
        text = (row.get(text_column) or "").strip()
        if not text:
            continue

        gt_entities = _parse_entities_raw(row.get("final_entities"))
        pred_entities = _parse_entities_raw(row.get(pred_column))

        spans = [
            Span(
                entity_type=ent["entity_type"],
                entity_value=ent.get("text", text[ent["start"]:ent["end"]]),
                start_position=ent["start"],
                end_position=ent["end"],
            )
            for ent in gt_entities
        ]

        sample = InputSample(
            full_text=text,
            spans=spans,
            create_tags_from_span=True,
            sample_id=idx,
        )

        pred_tags = span_to_tag(
            scheme="IO",
            text=text,
            starts=[ent["start"] for ent in pred_entities],
            ends=[ent["end"] for ent in pred_entities],
            tags=[ent["entity_type"] for ent in pred_entities],
            scores=[ent.get("score", 0.5) for ent in pred_entities],
            tokens=sample.tokens,
        )

        dataset.append(sample)
        all_predictions.append(pred_tags)
        row_indices.append(idx)

    # Collect all entity types
    all_entity_types: set[str] = set()
    for sample in dataset:
        for span in sample.spans:
            all_entity_types.add(span.entity_type)
    for pred_tags in all_predictions:
        for tag in pred_tags:
            if tag != "O":
                all_entity_types.add(tag)

    # Run SpanEvaluator
    evaluator = SpanEvaluator(
        model=None,
        entities_to_keep=list(all_entity_types) if all_entity_types else None,
        iou_threshold=0.5,
    )

    evaluation_results: list[EvaluationResult] = []
    for sample, pred_tags in zip(dataset, all_predictions):
        results, model_errors = evaluator.compare(
            input_sample=sample, prediction=pred_tags
        )
        evaluation_results.append(
            EvaluationResult(
                results=results,
                model_errors=model_errors,
                text=sample.full_text,
                tokens=[str(t) for t in sample.tokens],
                actual_tags=sample.tags,
                predicted_tags=pred_tags,
                start_indices=sample.start_indices,
            )
        )

    scores = evaluator.calculate_score(evaluation_results)

    # Overall metrics from SpanEvaluator
    overall_precision = round((scores.pii_precision or 0) * 100, 1)
    overall_recall = round((scores.pii_recall or 0) * 100, 1)
    overall_f1 = round((scores.pii_f or 0) * 100, 1)
    tp_total = scores.pii_true_positives or 0
    fp_total = scores.pii_false_positives or 0
    fn_total = scores.pii_false_negatives or 0

    # Per-entity breakdown from SpanEvaluator
    by_entity_type = []
    for etype in sorted(scores.per_type):
        metrics = scores.per_type[etype]
        by_entity_type.append({
            "type": etype,
            "precision": round((metrics.precision or 0) * 100, 1),
            "recall": round((metrics.recall or 0) * 100, 1),
            "f1": round((metrics.f_beta or 0) * 100, 1),
        })

    # Build entity-level misses for the Error Explorer UI
    misses: list[dict] = []
    for orig_idx, eval_result in zip(row_indices, evaluation_results):
        row = rows[orig_idx]
        record_id = f"rec-{orig_idx + 1:04d}"
        record_text = (row.get(text_column) or "").strip()

        for error in eval_result.model_errors:
            if error.error_type in ("FN", "FP"):
                entity_type = error.annotation if error.error_type == "FN" else error.prediction
                if entity_type == "O":
                    continue
                miss_type = MissType.false_negative if error.error_type == "FN" else MissType.false_positive
                misses.append(
                    EntityMiss(
                        record_id=record_id,
                        record_text=record_text,
                        missed_entity=Entity(
                            text=str(error.token),
                            entity_type=entity_type,
                            start=0,
                            end=len(str(error.token)),
                            score=None,
                        ),
                        miss_type=miss_type,
                        entity_type=entity_type,
                        risk_level=_risk_level(entity_type),
                    ).model_dump()
                )

    risk_counts = Counter(m["risk_level"] for m in misses)

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
            "high_risk": risk_counts.get(RiskLevel.high, 0),
            "medium_risk": risk_counts.get(RiskLevel.medium, 0),
            "low_risk": risk_counts.get(RiskLevel.low, 0),
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
        gold_entities = _parse_entities_raw(row.get("final_entities"))
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
