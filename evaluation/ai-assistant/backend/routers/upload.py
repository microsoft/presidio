"""Dataset load router — reads CSV and JSON files from a local path."""

from __future__ import annotations

import csv
import io
import json
import os
import shutil
import uuid

from fastapi import APIRouter, HTTPException
from models import (
    DatasetLoadRequest,
    DatasetRenameRequest,
    Entity,
    Record,
    UploadedDataset,
)

router = APIRouter(prefix="/api/datasets", tags=["datasets"])

# In-memory store for loaded datasets
_uploaded: dict[str, UploadedDataset] = {}
_records: dict[str, list[Record]] = {}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Persistence file for saved datasets (next to this file → backend/datasets.json)
_DATASETS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets.json")

# Local copy folder (gitignored)
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(_DATA_DIR, exist_ok=True)


def _save_registry() -> None:
    """Persist the dataset registry to disk."""
    data = [ds.model_dump() for ds in _uploaded.values()]
    with open(_DATASETS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _load_registry() -> None:
    """Load previously saved datasets from disk on startup."""
    if not os.path.isfile(_DATASETS_FILE):
        return
    try:
        with open(_DATASETS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            ds = UploadedDataset(**item)
            _uploaded[ds.id] = ds
    except Exception:
        pass  # ignore corrupt file


# Project root (evaluation/ai-assistant/) — used to resolve relative paths
_PROJECT_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)


def _resolve_path(path: str) -> str:
    """Resolve a path; relative paths are resolved against the project root."""
    if os.path.isabs(path):
        return path
    return os.path.normpath(os.path.join(_PROJECT_ROOT, path))


# Load on import so saved datasets are available immediately
_load_registry()


def _parse_entities(raw: str | list | None) -> list[Entity]:
    """Parse entities from a JSON string or list."""
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


def _parse_csv(
    content: str,
    text_column: str,
    entities_column: str | None,
) -> tuple[list[Record], list[str], bool]:
    """Parse CSV content into records."""
    reader = csv.DictReader(io.StringIO(content))
    fieldnames = list(reader.fieldnames or [])
    if text_column not in fieldnames:
        raise HTTPException(
            status_code=400,
            detail=f"CSV must have a '{text_column}' column. Found: {fieldnames}",
        )

    has_entities = entities_column is not None and entities_column in fieldnames
    has_final = "final_entities" in fieldnames
    records: list[Record] = []
    for i, row in enumerate(reader):
        text = row.get(text_column, "").strip()
        if not text:
            continue
        entities = (
            _parse_entities(row.get(entities_column))
            if has_entities and entities_column
            else []
        )
        final_ents = (
            _parse_entities(row.get("final_entities"))
            if has_final
            else None
        )
        records.append(
            Record(
                id=f"rec-{i + 1:04d}",
                text=text,
                dataset_entities=entities,
                final_entities=final_ents if final_ents else None,
            )
        )
    return records, fieldnames, has_entities, has_final


def _parse_json(
    content: str,
    text_column: str,
    entities_column: str | None,
) -> tuple[list[Record], list[str], bool]:
    """Parse JSON content (array of objects or JSONL) into records."""
    # Try parsing as a JSON array first
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Fall back to JSONL
        data = []
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not isinstance(data, list) or not data:
        raise HTTPException(
            status_code=400,
            detail="JSON file must contain an array of objects or be in JSONL format.",
        )

    records: list[Record] = []
    columns: set[str] = set()
    has_entities = False

    has_final = False
    for i, obj in enumerate(data):
        if not isinstance(obj, dict) or text_column not in obj:
            continue

        columns.update(obj.keys())
        text = str(obj[text_column]).strip()
        if not text:
            continue

        ent_raw = obj.get(entities_column) if entities_column else None
        entities = _parse_entities(ent_raw)
        if entities:
            has_entities = True

        final_raw = obj.get("final_entities")
        final_ents = _parse_entities(final_raw) if final_raw else None
        if final_ents:
            has_final = True

        records.append(
            Record(
                id=f"rec-{i + 1:04d}",
                text=text,
                dataset_entities=entities,
                final_entities=final_ents if final_ents else None,
            )
        )

    if not records:
        raise HTTPException(
            status_code=400,
            detail=(
                f"No valid records found. Each object must "
                f"have a '{text_column}' field."
            ),
        )
    return records, sorted(columns), has_entities, has_final


@router.get("/saved")
async def list_saved_datasets():
    """Return all saved datasets (for the dropdown)."""
    return list(_uploaded.values())


@router.post("/load")
async def load_dataset(req: DatasetLoadRequest):
    """Load a CSV or JSON file from a local absolute path."""
    if req.format not in ("csv", "json"):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported format '{req.format}'. "
                f"Only 'csv' and 'json' are supported."
            ),
        )

    file_path = os.path.expanduser(req.path)
    if not os.path.isabs(file_path):
        raise HTTPException(status_code=400, detail="Path must be absolute.")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=400, detail=f"File not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 50 MB)")

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    if req.format == "csv":
        records, columns, has_entities, has_final = _parse_csv(
            content, req.text_column, req.entities_column
        )
    else:
        records, columns, has_entities, has_final = _parse_json(
            content, req.text_column, req.entities_column
        )

    if not records:
        raise HTTPException(status_code=400, detail="No valid records found in file")

    dataset_id = f"upload-{uuid.uuid4().hex[:8]}"
    filename = os.path.basename(file_path)

    # Copy file to local data/ folder for persistence
    ext = os.path.splitext(filename)[1]
    stored_filename = f"{dataset_id}{ext}"
    stored_path = os.path.join(_DATA_DIR, stored_filename)
    shutil.copy2(file_path, stored_path)

    display_name = req.name.strip() if req.name and req.name.strip() else filename
    description = req.description.strip() if req.description else ""
    dataset = UploadedDataset(
        id=dataset_id,
        filename=filename,
        name=display_name,
        description=description,
        path=file_path,
        stored_path=stored_path,
        format=req.format,
        record_count=len(records),
        has_entities=has_entities,
        has_final_entities=has_final,
        columns=columns,
        text_column=req.text_column,
        entities_column=req.entities_column,
    )

    _uploaded[dataset_id] = dataset
    _records[dataset_id] = records
    _save_registry()

    return dataset


@router.patch("/{dataset_id}/rename")
async def rename_dataset(dataset_id: str, req: DatasetRenameRequest):
    """Rename a saved dataset."""
    if dataset_id not in _uploaded:
        raise HTTPException(status_code=404, detail="Dataset not found")
    new_name = req.name.strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    _uploaded[dataset_id] = _uploaded[dataset_id].model_copy(
        update={"name": new_name}
    )
    _save_registry()
    return _uploaded[dataset_id]


@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """Remove a saved dataset from the registry."""
    if dataset_id not in _uploaded:
        raise HTTPException(status_code=404, detail="Dataset not found")
    del _uploaded[dataset_id]
    _records.pop(dataset_id, None)
    _save_registry()
    return {"ok": True}


def _ensure_records_loaded(dataset_id: str) -> list[Record]:
    """Reload records from the stored copy (or original file) if not in memory."""
    if dataset_id in _records:
        return _records[dataset_id]
    ds = _uploaded.get(dataset_id)
    if ds is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    # Prefer the local stored copy; fall back to original path
    resolved = ds.stored_path if ds.stored_path and os.path.isfile(ds.stored_path) else _resolve_path(ds.path)
    if not os.path.isfile(resolved):
        raise HTTPException(
            status_code=404,
            detail=f"Source file no longer exists: {ds.path}",
        )
    with open(resolved, encoding="utf-8") as f:
        content = f.read()
    if ds.format == "csv":
        records, _, _, _ = _parse_csv(content, ds.text_column, ds.entities_column)
    else:
        records, _, _, _ = _parse_json(content, ds.text_column, ds.entities_column)
    _records[dataset_id] = records
    return records


@router.get("/{dataset_id}/records")
async def get_dataset_records(dataset_id: str):
    """Return parsed records for a loaded dataset."""
    return _ensure_records_loaded(dataset_id)


@router.get("/{dataset_id}/preview")
async def preview_dataset(dataset_id: str, limit: int = 5):
    """Return a small preview of the loaded dataset."""
    records = _ensure_records_loaded(dataset_id)
    return records[:limit]
