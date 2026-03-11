"""LLM Judge router — configure and run LLM-based PII detection."""

from __future__ import annotations

import asyncio
import logging
import time

import llm_service
from fastapi import APIRouter, HTTPException
from models import LLMAnalyzeRequest, LLMConfig
from settings import MODEL_CHOICES, load_from_env

from routers.upload import _ensure_records_loaded

router = APIRouter(prefix="/api/llm", tags=["llm"])
logger = logging.getLogger(__name__)

# Currently selected deployment (persisted across page reloads while server lives)
_selected_deployment: str | None = None

# Active dataset for current analysis run
_active_dataset_id: str | None = None

# In-memory state for the current LLM analysis run
_state: dict = {
    "progress": 0,
    "total": 0,
    "running": False,
    "error": None,
    "results": {},  # record_id -> list[Entity dict]
    "start_time": None,
    "elapsed_ms": None,
}


def _env_is_ready() -> bool:
    """Check if .env has the required Azure endpoint."""
    env = load_from_env()
    return bool(env.azure_endpoint)


# ── Model catalogue ──────────────────────────────────────


@router.get("/models")
async def list_models():
    """Return available model choices for the UI dropdown."""
    return MODEL_CHOICES


# ── Settings ─────────────────────────────────────────────


@router.get("/settings")
async def get_settings():
    """Return current LLM Judge configuration (no secrets)."""
    env = load_from_env()
    return {
        "env_ready": bool(env.azure_endpoint),
        "has_endpoint": bool(env.azure_endpoint),
        "has_api_key": bool(env.azure_api_key),
        "auth_method": "api_key" if env.azure_api_key else "default_credential",
        "deployment_name": _selected_deployment or env.deployment_name,
        "configured": llm_service.is_configured(),
    }


@router.post("/configure")
async def configure_llm(config: LLMConfig):
    """Configure the LLM recognizer using .env credentials + chosen deployment."""
    global _selected_deployment

    env = load_from_env()
    if not env.azure_endpoint:
        raise HTTPException(
            status_code=400,
            detail=(
                "PRESIDIO_EVAL_AZURE_ENDPOINT must be set in backend/.env "
                "before configuring the LLM Judge."
            ),
        )

    # Validate the chosen deployment is in our allowed list
    allowed_ids = {m["id"] for m in MODEL_CHOICES}
    deployment = config.deployment_name
    if deployment not in allowed_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Deployment '{deployment}' is not in the allowed list.",
        )

    try:
        result = llm_service.configure(
            azure_endpoint=env.azure_endpoint,
            api_key=env.azure_api_key,  # None → DefaultAzureCredential
            deployment_name=deployment,
            api_version=env.api_version,
        )
    except llm_service.LLMServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _selected_deployment = deployment
    return result


@router.post("/disconnect")
async def disconnect_llm():
    """Disconnect the LLM recognizer and reset analysis state."""
    global _selected_deployment, _active_dataset_id
    llm_service.disconnect()
    _selected_deployment = None
    _active_dataset_id = None
    _state["progress"] = 0
    _state["total"] = 0
    _state["running"] = False
    _state["error"] = None
    _state["results"] = {}
    _state["start_time"] = None
    _state["elapsed_ms"] = None
    return {"status": "disconnected"}


# ── Status / analysis ────────────────────────────────────


@router.get("/status")
async def get_llm_status():
    """Return LLM configuration and analysis status."""
    entity_count = sum(len(ents) for ents in _state["results"].values())
    return {
        "configured": llm_service.is_configured(),
        "running": _state["running"],
        "progress": _state["progress"],
        "total": _state["total"],
        "error": _state["error"],
        "entity_count": entity_count,
        "elapsed_ms": _state["elapsed_ms"],
    }


@router.post("/analyze")
async def start_llm_analysis(req: LLMAnalyzeRequest):
    """Run LLM analysis on all records of a dataset."""
    global _active_dataset_id

    if not llm_service.is_configured():
        raise HTTPException(
            status_code=400,
            detail="LLM not configured. POST /api/llm/configure first.",
        )

    if _state["running"]:
        raise HTTPException(status_code=409, detail="Analysis already running.")

    records = _ensure_records_loaded(req.dataset_id)
    if not records:
        raise HTTPException(
            status_code=400,
            detail=f"No records found for dataset '{req.dataset_id}'.",
        )

    _active_dataset_id = req.dataset_id
    _state["progress"] = 0
    _state["total"] = len(records)
    _state["running"] = True
    _state["error"] = None
    _state["results"] = {}
    _state["start_time"] = time.time()
    _state["elapsed_ms"] = None

    asyncio.create_task(_run_analysis())
    return {"status": "started", "total": _state["total"]}


async def _run_analysis():
    """Background task: analyse each record via the LLM."""
    loop = asyncio.get_event_loop()
    records = _ensure_records_loaded(_active_dataset_id) if _active_dataset_id else []
    try:
        for record in records:
            try:
                entities = await loop.run_in_executor(
                    None, llm_service.analyze_text, record.text
                )
                entity_dicts = [e.model_dump() for e in entities]
                _state["results"][record.id] = entity_dicts
                if entity_dicts:
                    summary = "; ".join(
                        f"{e['entity_type']}('{e['text']}' @{e['start']}-{e['end']})"
                        for e in entity_dicts
                    )
                    logger.info("[LLM] %s: %s", record.id, summary)
                else:
                    logger.info("[LLM] %s: no entities", record.id)
            except Exception:
                logger.exception("LLM analysis failed for record %s", record.id)
                _state["results"][record.id] = []
            _state["progress"] += 1
    except Exception as exc:
        logger.exception("LLM analysis task failed")
        _state["error"] = str(exc)
    finally:
        _state["running"] = False
        if _state["start_time"]:
            _state["elapsed_ms"] = round((time.time() - _state["start_time"]) * 1000)


@router.get("/results")
async def get_llm_results():
    """Return LLM entities for all analysed records."""
    return _state["results"]


@router.get("/results/{record_id}")
async def get_llm_record_results(record_id: str):
    """Return LLM entities for a specific record."""
    entities = _state["results"].get(record_id)
    if entities is None:
        raise HTTPException(status_code=404, detail="Record not found in results.")
    return entities
