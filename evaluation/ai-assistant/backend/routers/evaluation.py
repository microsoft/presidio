from __future__ import annotations

import json
import logging
from collections import Counter
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException
from models import Entity, EntityMiss, MissType, RiskLevel
from presidio_evaluator import InputSample, Span, span_to_tag
from presidio_evaluator.evaluation import EvaluationResult, SpanEvaluator

from routers.upload import _uploaded

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])

logger = logging.getLogger(__name__)

# High-risk entity types whose misses are flagged as "high" risk.
_HIGH_RISK_TYPES: set[str] = {
    "CREDIT_CARD",
    "US_SSN",
    "SSN",
    "US_BANK_NUMBER",
    "IBAN_CODE",
    "MEDICAL_LICENSE",
}


# ---------------------------------------------------------------------------
# SpanEvaluator helpers
# ---------------------------------------------------------------------------


def _parse_entities(raw):
    """Parse the entity column from string or list."""
    if isinstance(raw, str):
        return json.loads(raw)
    if isinstance(raw, list):
        return raw
    return []


def _row_to_input_sample(row, idx):
    """Create an InputSample from a row using final_entities."""
    text = row["text"]
    gt_entities = _parse_entities(row["final_entities"])

    spans = [
        Span(
            entity_type=ent["entity_type"],
            entity_value=ent["text"],
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
    return sample


def _row_to_prediction_tags(row, sample):
    """Convert presidio_analyzer_entities to per-token IO tags."""
    pred_entities = _parse_entities(row["presidio_analyzer_entities"])

    starts = [ent["start"] for ent in pred_entities]
    ends = [ent["end"] for ent in pred_entities]
    tags = [ent["entity_type"] for ent in pred_entities]
    scores = [ent.get("score", 0.5) for ent in pred_entities]

    prediction_tags = span_to_tag(
        scheme="IO",
        text=sample.full_text,
        starts=starts,
        ends=ends,
        tags=tags,
        scores=scores,
        tokens=sample.tokens,
    )
    return prediction_tags


def _find_prediction_column(df: pd.DataFrame) -> str:
    """Find the prediction column in the DataFrame."""
    if "presidio_analyzer_entities" in df.columns:
        return "presidio_analyzer_entities"
    config_cols = [c for c in df.columns if c.startswith("config_")]
    if config_cols:
        return config_cols[0]
    raise ValueError(
        "No prediction column found. "
        "Expected 'presidio_analyzer_entities' or a 'config_*' column."
    )


def _find_dataset_csv() -> Path:
    """Find the stored CSV that has final_entities."""
    for ds in _uploaded.values():
        if ds.has_final_entities and ds.stored_path:
            return Path(ds.stored_path)
    for ds in _uploaded.values():
        if ds.stored_path:
            return Path(ds.stored_path)
    raise ValueError("No uploaded dataset found.")


def _risk_level(entity_type: str) -> RiskLevel:
    if entity_type in _HIGH_RISK_TYPES:
        return RiskLevel.high
    return RiskLevel.medium


def _spans_overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return a_start < b_end and b_start < a_end


# ---------------------------------------------------------------------------
# Core evaluation using presidio-evaluator SpanEvaluator
# ---------------------------------------------------------------------------


def _run_evaluation() -> dict:
    """Run evaluation using presidio-evaluator's SpanEvaluator.

    Reads the saved CSV with ``final_entities`` (ground truth) and a
    prediction column, builds InputSample / prediction-tag pairs, then
    delegates scoring to ``SpanEvaluator``.
    """
    csv_path = _find_dataset_csv()
    df = pd.read_csv(csv_path)

    if "final_entities" not in df.columns:
        raise ValueError("CSV is missing the 'final_entities' column.")

    pred_col = _find_prediction_column(df)
    if pred_col != "presidio_analyzer_entities":
        df = df.rename(columns={pred_col: "presidio_analyzer_entities"})

    # Build dataset and predictions
    dataset: list[InputSample] = []
    all_predictions: list[list[str]] = []

    for i, (_, row) in enumerate(df.iterrows()):
        sample = _row_to_input_sample(row, i)
        pred_tags = _row_to_prediction_tags(row, sample)
        dataset.append(sample)
        all_predictions.append(pred_tags)

    logger.info("Converted %d rows into InputSample objects", len(dataset))

    # Collect all entity types from both ground truth and predictions
    all_entity_types: set[str] = set()
    for sample in dataset:
        for span in sample.spans:
            all_entity_types.add(span.entity_type)
    for pred_tags in all_predictions:
        for tag in pred_tags:
            if tag != "O":
                all_entity_types.add(tag)

    # Identity mapping (dataset and model use the same entity names)
    entity_mapping = {e: e for e in all_entity_types}

    # Create the evaluator without a model (we already have predictions)
    evaluator = SpanEvaluator(
        model=None,
        entity_mapping=entity_mapping,
        iou_threshold=0.5,
    )

    # Build EvaluationResult objects
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

    # Calculate aggregate scores
    scores = evaluator.calculate_score(evaluation_results)

    overall_precision = round((scores.pii_precision or 0) * 100)
    overall_recall = round((scores.pii_recall or 0) * 100)
    overall_f1 = round((scores.pii_f or 0) * 100)

    # Per-entity-type breakdown from SpanEvaluator results
    all_scored_types = set(
        list(scores.entity_precision_dict.keys())
        + list(scores.entity_recall_dict.keys())
    )
    by_entity: list[dict] = []
    for etype in sorted(all_scored_types):
        e_prec = scores.entity_precision_dict.get(etype, 0) or 0
        e_rec = scores.entity_recall_dict.get(etype, 0) or 0
        e_f1 = (
            2 * e_prec * e_rec / (e_prec + e_rec)
            if (e_prec + e_rec)
            else 0
        )
        by_entity.append(
            {
                "type": etype,
                "precision": round(e_prec * 100),
                "recall": round(e_rec * 100),
                "f1": round(e_f1 * 100),
            }
        )

    # Build entity-level misses from raw span data for the Error Explorer
    misses: list[EntityMiss] = []
    fn_counter: Counter[str] = Counter()
    fp_counter: Counter[str] = Counter()

    for i, (_, row) in enumerate(df.iterrows()):
        text = row["text"]
        rec_id = f"rec-{i + 1:04d}"
        gt_ents = _parse_entities(row["final_entities"])
        pred_ents = _parse_entities(row["presidio_analyzer_entities"])

        # Greedy span matching to identify FP / FN at entity level
        matched_gt: set[int] = set()
        matched_pred: set[int] = set()
        for gi, gt in enumerate(gt_ents):
            for pi, pr in enumerate(pred_ents):
                if pi in matched_pred:
                    continue
                if gt["entity_type"] == pr["entity_type"] and _spans_overlap(
                    gt["start"], gt["end"], pr["start"], pr["end"]
                ):
                    matched_gt.add(gi)
                    matched_pred.add(pi)
                    break

        for gi, gt in enumerate(gt_ents):
            if gi not in matched_gt:
                fn_counter[gt["entity_type"]] += 1
                misses.append(
                    EntityMiss(
                        record_id=rec_id,
                        record_text=text,
                        missed_entity=Entity(
                            text=gt.get("text", text[gt["start"] : gt["end"]]),
                            entity_type=gt["entity_type"],
                            start=gt["start"],
                            end=gt["end"],
                            score=gt.get("score"),
                        ),
                        miss_type=MissType.false_negative,
                        entity_type=gt["entity_type"],
                        risk_level=_risk_level(gt["entity_type"]),
                    )
                )

        for pi, pr in enumerate(pred_ents):
            if pi not in matched_pred:
                fp_counter[pr["entity_type"]] += 1
                misses.append(
                    EntityMiss(
                        record_id=rec_id,
                        record_text=text,
                        missed_entity=Entity(
                            text=pr.get("text", text[pr["start"] : pr["end"]]),
                            entity_type=pr["entity_type"],
                            start=pr["start"],
                            end=pr["end"],
                            score=pr.get("score"),
                        ),
                        miss_type=MissType.false_positive,
                        entity_type=pr["entity_type"],
                        risk_level=_risk_level(pr["entity_type"]),
                    )
                )

    fn_count = sum(fn_counter.values())
    fp_count = sum(fp_counter.values())

    def _top_counts(counter: Counter[str], top_n: int = 5) -> list[dict]:
        return [{"type": t, "count": c} for t, c in counter.most_common(top_n)]

    return {
        "overall": {
            "precision": overall_precision,
            "recall": overall_recall,
            "f1_score": overall_f1,
            "false_negatives": fn_count,
        },
        "by_entity_type": by_entity,
        "errors": {
            "false_negatives": {
                "total": fn_count,
                "by_type": _top_counts(fn_counter),
            },
            "false_positives": {
                "total": fp_count,
                "by_type": _top_counts(fp_counter),
            },
        },
        "misses": misses,
    }


# ---------------------------------------------------------------------------
# Cached evaluation state
# ---------------------------------------------------------------------------
_last_eval: dict | None = None


def _ensure_evaluation() -> dict:
    """Compute evaluation if not cached, or return cached result."""
    global _last_eval
    if _last_eval is not None:
        return _last_eval
    try:
        _last_eval = _run_evaluation()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _last_eval


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/run")
async def trigger_evaluation():
    """Trigger a fresh evaluation run."""
    global _last_eval
    _last_eval = None
    result = _ensure_evaluation()
    return {
        "status": "complete",
        "overall": result["overall"],
        "miss_count": len(result["misses"]),
    }


@router.get("/misses", response_model=list[EntityMiss])
async def get_entity_misses(
    miss_type: str | None = None,
    entity_type: str | None = None,
    risk_level: str | None = None,
):
    """Return entity misses with optional filtering."""
    result = _ensure_evaluation()
    misses: list[EntityMiss] = result["misses"]
    if miss_type and miss_type != "all":
        misses = [m for m in misses if m.miss_type == miss_type]
    if entity_type and entity_type != "all":
        misses = [m for m in misses if m.entity_type == entity_type]
    if risk_level and risk_level != "all":
        misses = [m for m in misses if m.risk_level == risk_level]
    return misses


@router.get("/metrics")
async def get_metrics():
    """Return overall and per-entity-type metrics."""
    result = _ensure_evaluation()
    return {
        "overall": result["overall"],
        "by_entity_type": result["by_entity_type"],
        "errors": result["errors"],
    }


@router.get("/patterns")
async def get_error_patterns():
    """Return error patterns and insights derived from evaluation misses."""
    result = _ensure_evaluation()
    misses: list[EntityMiss] = result["misses"]

    # Build frequent-miss summary
    fn_misses = [m for m in misses if m.miss_type == MissType.false_negative]
    fn_counter: Counter[str] = Counter(m.entity_type for m in fn_misses)
    frequent_misses = [
        {"type": etype, "count": count, "pattern": f"{count} missed {etype} entities"}
        for etype, count in fn_counter.most_common(10)
    ]

    # Build insights from the data
    insights: list[dict] = []
    by_entity = result["by_entity_type"]

    # Flag entity types with low recall
    low_recall = [e for e in by_entity if e["recall"] < 80]
    if low_recall:
        types_str = ", ".join(f"{e['type']} ({e['recall']}%)" for e in low_recall)
        insights.append(
            {
                "title": "Low Recall Entity Types",
                "description": (
                    "The following entity types have recall below "
                    f"80%: {types_str}. Consider adding custom "
                    "recognizers or adjusting thresholds."
                ),
            }
        )

    # Flag entity types with low precision
    low_prec = [e for e in by_entity if e["precision"] < 80]
    if low_prec:
        types_str = ", ".join(f"{e['type']} ({e['precision']}%)" for e in low_prec)
        insights.append(
            {
                "title": "Low Precision Entity Types",
                "description": (
                    "The following entity types have precision "
                    f"below 80%: {types_str}. Consider raising "
                    "thresholds or refining recognizer patterns."
                ),
            }
        )

    # Highlight strong performers
    strong = [e for e in by_entity if e["f1"] >= 90]
    if strong:
        types_str = ", ".join(f"{e['type']} (F1={e['f1']}%)" for e in strong)
        insights.append(
            {
                "title": "Strong Performers",
                "description": (
                    f"These entity types are performing well: {types_str}. "
                    "No tuning needed."
                ),
            }
        )

    # High-risk misses
    high_risk = [m for m in fn_misses if m.risk_level == RiskLevel.high]
    if high_risk:
        hr_counter: Counter[str] = Counter(m.entity_type for m in high_risk)
        hr_str = ", ".join(f"{c} {t}" for t, c in hr_counter.most_common())
        insights.append(
            {
                "title": "High-Risk False Negatives",
                "description": (
                    f"{len(high_risk)} high-risk entities were missed: {hr_str}. "
                    "Prioritize improving detection for these types."
                ),
            }
        )

    if not insights:
        insights.append(
            {
                "title": "No Issues Detected",
                "description": (
                    "All entity types are performing "
                    "within acceptable ranges."
                ),
            }
        )

    return {
        "frequent_misses": frequent_misses,
        "common_patterns": [],
        "insights": insights,
    }
