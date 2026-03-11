"""Presidio Analyzer router — simple in-process engine, no multiprocessing."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import shutil
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

from routers.upload import _ensure_records_loaded

router = APIRouter(prefix="/api/presidio", tags=["presidio"])
logger = logging.getLogger(__name__)
_NAME_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9 _.\-]*$')

# ---------------------------------------------------------------------------
# Named configs storage
# ---------------------------------------------------------------------------
_CONFIGS_FILE = Path(__file__).resolve().parent.parent / "data" / "presidio_configs.json"

_BUILTIN_CONFIGS: list[dict] = [
    {"name": "default_spacy", "path": None},
]


def _load_saved_configs() -> list[dict]:
    """Return list of {name, path} dicts (builtins + user-saved)."""
    user_configs: list[dict] = []
    if _CONFIGS_FILE.exists():
        try:
            user_configs = json.loads(_CONFIGS_FILE.read_text())
        except Exception:
            user_configs = []
    return _BUILTIN_CONFIGS + user_configs


def _save_user_configs(configs: list[dict]) -> None:
    _CONFIGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CONFIGS_FILE.write_text(json.dumps(configs, indent=2))


def _get_user_configs() -> list[dict]:
    if _CONFIGS_FILE.exists():
        try:
            return json.loads(_CONFIGS_FILE.read_text())
        except Exception:
            return []
    return []


# ---------------------------------------------------------------------------
# Per-config results accumulator (replaces run snapshots)
# ---------------------------------------------------------------------------
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# config_name -> {rec_id -> entities}
_all_config_results: dict[str, dict[str, list]] = {}


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
_engine = None  # lazy-loaded AnalyzerEngine singleton

_state: dict = {
    "configured": False,
    "loading": False,
    "config_name": None,
    "config_path": None,
    "running": False,
    "progress": 0,
    "total": 0,
    "error": None,
    "results": {},
    "start_time": None,
    "elapsed_ms": None,
}


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class PresidioConfigureRequest(BaseModel):
    config_name: str | None = None
    config_path: str | None = None


class PresidioAnalyzeRequest(BaseModel):
    dataset_id: str


class PresidioSaveConfigRequest(BaseModel):
    name: str
    path: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Config CRUD
# ---------------------------------------------------------------------------
@router.get("/configs")
async def list_configs():
    return _load_saved_configs()


@router.post("/configs")
async def save_config(req: PresidioSaveConfigRequest):
    name = req.name.strip()
    path = req.path.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Config name is required.")
    if not _NAME_RE.match(name):
        raise HTTPException(status_code=400, detail="Name may only contain letters, numbers, hyphens, underscores, dots, and spaces.")
    if not path:
        raise HTTPException(status_code=400, detail="Config path is required.")
    if not os.path.isabs(path):
        raise HTTPException(status_code=400, detail="Config path must be absolute.")
    if not os.path.isfile(path):
        raise HTTPException(status_code=400, detail=f"Config file not found: {path}")

    # Copy the config file into our data/ folder so we own the copy
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = name.replace(" ", "_").replace("/", "_")
    dest = _DATA_DIR / f"config-{safe_name}.yml"
    shutil.copy2(path, dest)
    abs_path = str(dest.resolve())

    user_configs = _get_user_configs()
    # Replace if same name exists
    user_configs = [c for c in user_configs if c["name"] != name]
    user_configs.append({"name": name, "path": abs_path})
    _save_user_configs(user_configs)
    return {"status": "saved", "configs": _load_saved_configs()}


@router.delete("/configs/{config_name}")
async def delete_config(config_name: str):
    user_configs = _get_user_configs()
    # Find the config to delete (so we can clean up its file)
    to_delete = [c for c in user_configs if c["name"] == config_name]
    remaining = [c for c in user_configs if c["name"] != config_name]
    if len(remaining) == len(user_configs):
        raise HTTPException(status_code=404, detail="Config not found.")
    # Remove the stored config file if it lives in our data/ folder
    for cfg in to_delete:
        cfg_path = cfg.get("path", "")
        if cfg_path and _DATA_DIR.resolve() in Path(cfg_path).resolve().parents:
            try:
                os.remove(cfg_path)
            except OSError:
                pass
    _save_user_configs(remaining)
    return {"status": "deleted", "configs": _load_saved_configs()}


@router.post("/configs/upload")
async def upload_config(
    file: UploadFile = File(...),
    name: str = Form(...),
):
    """Upload a YAML config file and save it with a given name."""
    if not file.filename or not file.filename.lower().endswith((".yml", ".yaml")):
        raise HTTPException(status_code=400, detail="Only .yml / .yaml files are accepted.")
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Config name is required.")
    if not _NAME_RE.match(name):
        raise HTTPException(status_code=400, detail="Name may only contain letters, numbers, hyphens, underscores, dots, and spaces.")

    content = await file.read()
    if len(content) > 1 * 1024 * 1024:  # 1 MB limit
        raise HTTPException(status_code=400, detail="Config file too large (max 1 MB).")

    # Save the uploaded file to data/ folder
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = name.replace(" ", "_").replace("/", "_")
    dest = _DATA_DIR / f"config-{safe_name}.yml"
    dest.write_bytes(content)
    abs_path = str(dest.resolve())

    # Save to config registry
    user_configs = _get_user_configs()
    user_configs = [c for c in user_configs if c["name"] != name]
    user_configs.append({"name": name, "path": abs_path})
    _save_user_configs(user_configs)

    return {"status": "saved", "path": abs_path, "configs": _load_saved_configs()}


# ---------------------------------------------------------------------------
# Configure / Load engine
# ---------------------------------------------------------------------------
@router.post("/configure")
async def configure_presidio(req: PresidioConfigureRequest):
    global _engine

    if req.config_path:
        if not os.path.isabs(req.config_path):
            raise HTTPException(status_code=400, detail="Config path must be an absolute path.")
        if not os.path.isfile(req.config_path):
            raise HTTPException(status_code=400, detail=f"Config file not found: {req.config_path}")

    # Reset
    _engine = None
    _state["loading"] = True
    _state["configured"] = False
    _state["error"] = None
    _state["config_name"] = req.config_name or ("default" if not req.config_path else None)
    _state["config_path"] = req.config_path

    # Load the engine in a background thread so we don't block the event loop
    asyncio.create_task(_load_engine(req.config_path))

    return {"status": "loading", "config_path": req.config_path or "default"}


async def _load_engine(config_path: str | None):
    """Initialise AnalyzerEngine in a thread (model download can be slow)."""
    global _engine
    loop = asyncio.get_event_loop()
    try:
        _engine = await loop.run_in_executor(None, _create_engine, config_path)
        _state["configured"] = True
        _state["loading"] = False
        logger.info("Presidio AnalyzerEngine ready (config=%s)", config_path or "default")
    except Exception as exc:
        logger.exception("Failed to initialise Presidio engine")
        _state["error"] = str(exc)
        _state["loading"] = False


def _create_engine(config_path: str | None):
    """Synchronous factory — runs inside run_in_executor."""
    try:
        from presidio_analyzer import AnalyzerEngine
        from presidio_analyzer.analyzer_engine_provider import AnalyzerEngineProvider
    except ImportError as exc:
        raise RuntimeError(
            "presidio-analyzer is not installed. "
            "Run: cd backend && poetry install"
        ) from exc

    if config_path:
        provider = AnalyzerEngineProvider(analyzer_engine_conf_file=config_path)
        return provider.create_engine()
    return AnalyzerEngine()


@router.get("/status")
async def get_presidio_status():
    entity_count = sum(len(ents) for ents in _state["results"].values())
    return {
        "configured": _state["configured"],
        "loading": _state["loading"],
        "config_name": _state["config_name"],
        "config_path": _state["config_path"] or "default",
        "running": _state["running"],
        "progress": _state["progress"],
        "total": _state["total"],
        "error": _state["error"],
        "entity_count": entity_count,
        "elapsed_ms": _state["elapsed_ms"],
    }


@router.post("/analyze")
async def start_presidio_analysis(req: PresidioAnalyzeRequest):
    if not _state["configured"] or _engine is None:
        raise HTTPException(status_code=400, detail="Presidio not configured. POST /api/presidio/configure first.")

    if _state["running"]:
        raise HTTPException(status_code=409, detail="Analysis already running.")

    records = _ensure_records_loaded(req.dataset_id)
    if not records:
        raise HTTPException(status_code=400, detail=f"No records found for dataset '{req.dataset_id}'.")

    _state["progress"] = 0
    _state["total"] = len(records)
    _state["running"] = True
    _state["error"] = None
    _state["results"] = {}
    _state["start_time"] = time.time()
    _state["elapsed_ms"] = None

    asyncio.create_task(_run_analysis(req.dataset_id))
    return {"status": "started", "total": _state["total"]}


async def _run_analysis(dataset_id: str):
    """Analyse each record using the engine in a thread."""
    loop = asyncio.get_event_loop()
    records = _ensure_records_loaded(dataset_id)

    try:
        for record in records:
            entities = await loop.run_in_executor(None, _analyze_record, record.text)
            _state["results"][record.id] = entities
            _state["progress"] += 1
            if entities:
                summary = "; ".join(
                    f"{e['entity_type']}('{e['text']}' @{e['start']}-{e['end']} score={e['score']})"
                    for e in entities
                )
                logger.info("[Presidio] %s: %s", record.id, summary)
            else:
                logger.info("[Presidio] %s: no entities", record.id)
    except Exception as exc:
        logger.exception("Presidio analysis task failed")
        _state["error"] = str(exc)
    finally:
        _state["running"] = False
        if _state["start_time"]:
            _state["elapsed_ms"] = round((time.time() - _state["start_time"]) * 1000)
        # Accumulate results under the config name
        if _state["error"] is None and _state["results"] and _state["config_name"]:
            _all_config_results[_state["config_name"]] = dict(_state["results"])


def _analyze_record(text: str) -> list[dict]:
    """Synchronous single-record analysis — runs inside run_in_executor."""
    results = _engine.analyze(text=text, language="en")
    return [
        {
            "text": text[r.start : r.end],
            "entity_type": r.entity_type,
            "start": r.start,
            "end": r.end,
            "score": round(r.score, 4),
        }
        for r in results
    ]


@router.get("/results")
async def get_presidio_results():
    return _state["results"]


@router.get("/results/{record_id}")
async def get_presidio_record_results(record_id: str):
    entities = _state["results"].get(record_id)
    if entities is None:
        raise HTTPException(status_code=404, detail="Record not found in results.")
    return entities


@router.post("/disconnect")
async def disconnect_presidio():
    global _engine
    _engine = None
    _state["configured"] = False
    _state["loading"] = False
    _state["config_name"] = None
    _state["config_path"] = None
    _state["running"] = False
    _state["progress"] = 0
    _state["total"] = 0
    _state["error"] = None
    _state["results"] = {}
    _state["start_time"] = None
    _state["elapsed_ms"] = None
    return {"status": "disconnected"}


@router.get("/configs/{config_name}/download")
async def download_config(config_name: str):
    """Download the YAML file for a named config."""
    all_configs = _load_saved_configs()
    cfg = next((c for c in all_configs if c["name"] == config_name), None)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Config not found")
    cfg_path = cfg.get("path")
    # For built-in configs without a file (e.g. default_spacy), serve the
    # bundled default.yaml shipped with presidio-analyzer.
    if not cfg_path or not Path(cfg_path).is_file():
        try:
            import presidio_analyzer
            pkg_dir = Path(presidio_analyzer.__file__).parent
            default_yaml = pkg_dir / "conf" / "default.yaml"
            if default_yaml.is_file():
                return FileResponse(
                    str(default_yaml),
                    media_type="application/x-yaml",
                    filename=f"{config_name}.yml",
                )
        except ImportError:
            pass
        raise HTTPException(status_code=404, detail="Config file not found on disk")
    return FileResponse(
        cfg_path,
        media_type="application/x-yaml",
        filename=f"{config_name}.yml",
    )
