"""Dataset load router — reads CSV and JSON files from a local path."""

from __future__ import annotations

import csv
import io
import json
import os
import uuid

from fastapi import APIRouter, HTTPException

from models import DatasetLoadRequest, Entity, Record, UploadedDataset

router = APIRouter(prefix="/api/datasets", tags=["datasets"])

# In-memory store for loaded datasets
_uploaded: dict[str, UploadedDataset] = {}
_records: dict[str, list[Record]] = {}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


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
    records: list[Record] = []
    for i, row in enumerate(reader):
        text = row.get(text_column, "").strip()
        if not text:
            continue
        entities = _parse_entities(row.get(entities_column)) if has_entities and entities_column else []
        records.append(
            Record(
                id=f"rec-{i + 1:04d}",
                text=text,
                dataset_entities=entities,
            )
        )
    return records, fieldnames, has_entities


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

        records.append(
            Record(
                id=f"rec-{i + 1:04d}",
                text=text,
                dataset_entities=entities,
            )
        )

    if not records:
        raise HTTPException(
            status_code=400,
            detail=f"No valid records found. Each object must have a '{text_column}' field.",
        )
    return records, sorted(columns), has_entities


@router.post("/load")
async def load_dataset(req: DatasetLoadRequest):
    """Load a CSV or JSON file from a local absolute path."""
    if req.format not in ("csv", "json"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{req.format}'. Only 'csv' and 'json' are supported.",
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
        records, columns, has_entities = _parse_csv(content, req.text_column, req.entities_column)
    else:
        records, columns, has_entities = _parse_json(content, req.text_column, req.entities_column)

    if not records:
        raise HTTPException(status_code=400, detail="No valid records found in file")

    dataset_id = f"upload-{uuid.uuid4().hex[:8]}"
    filename = os.path.basename(file_path)
    dataset = UploadedDataset(
        id=dataset_id,
        filename=filename,
        format=req.format,
        record_count=len(records),
        has_entities=has_entities,
        columns=columns,
    )

    _uploaded[dataset_id] = dataset
    _records[dataset_id] = records

    return dataset


@router.get("/{dataset_id}/records")
async def get_dataset_records(dataset_id: str):
    """Return parsed records for a loaded dataset."""
    if dataset_id not in _records:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return _records[dataset_id]


@router.get("/{dataset_id}/preview")
async def preview_dataset(dataset_id: str, limit: int = 5):
    """Return a small preview of the loaded dataset."""
    if dataset_id not in _records:
        raise HTTPException(status_code=404, detail="Dataset not found")
    records = _records[dataset_id][:limit]
    return records
