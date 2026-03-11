from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models import Entity, EntityAction, Record
from routers.upload import _records as uploaded_records, _uploaded, _save_registry
from routers.presidio_service import _state as presidio_state

router = APIRouter(prefix="/api/review", tags=["review"])

# In-memory golden set: record_id -> confirmed entities
_golden_set: dict[str, list[Entity]] = {}
_reviewed: set[str] = set()
# Active dataset for review
_active_dataset_id: str | None = None


def set_active_dataset(dataset_id: str) -> None:
    """Set the dataset used for review (called by other routers)."""
    global _active_dataset_id
    _active_dataset_id = dataset_id


def _get_review_records() -> list[Record]:
    """Get records for the active dataset."""
    if _active_dataset_id and _active_dataset_id in uploaded_records:
        return uploaded_records[_active_dataset_id]
    # Return first available dataset if no active one set
    for records in uploaded_records.values():
        return records
    return []


@router.get("/records", response_model=list[Record])
async def get_review_records():
    """List records for human review."""
    return _get_review_records()


@router.post("/records/{record_id}/confirm")
async def confirm_entity(record_id: str, action: EntityAction):
    """Confirm an entity and add it to the golden set."""
    _golden_set.setdefault(record_id, []).append(action.entity)
    _reviewed.add(record_id)
    return {"status": "confirmed", "record_id": record_id}


def _spans_overlap(a: Entity, b: Entity) -> bool:
    """Return True if two entity spans overlap."""
    return a.start < b.end and b.start < a.end


@router.post("/records/{record_id}/reject")
async def reject_entity(record_id: str, action: EntityAction):
    """Reject an entity and remove it from the golden set."""
    entities = _golden_set.get(record_id, [])
    _golden_set[record_id] = [
        e
        for e in entities
        if not _spans_overlap(e, action.entity)
    ]
    _reviewed.add(record_id)
    return {"status": "rejected", "record_id": record_id}


@router.post("/records/{record_id}/manual")
async def add_manual_entity(record_id: str, action: EntityAction):
    """Manually add an entity to the golden set."""
    entity = action.entity.model_copy(update={"score": 1.0})
    _golden_set.setdefault(record_id, []).append(entity)
    _reviewed.add(record_id)
    return {"status": "added", "record_id": record_id}


@router.get("/progress")
async def get_review_progress():
    """Return review completion progress."""
    total = len(_get_review_records())
    reviewed = len(_reviewed)
    return {
        "total": total,
        "reviewed": reviewed,
        "progress": (reviewed / total * 100) if total else 0,
        "golden_set_size": sum(len(v) for v in _golden_set.values()),
    }


@router.get("/golden-set")
async def get_golden_set():
    """Return the current golden entity set."""
    return _golden_set


class SaveFinalEntitiesRequest(BaseModel):
    dataset_id: str
    golden_set: dict[str, list[dict]]


@router.post("/save-final-entities")
async def save_final_entities(req: SaveFinalEntitiesRequest):
    """Persist the human-approved golden set as final_entities in the stored dataset file."""
    import csv
    import io
    import json
    import os

    ds = _uploaded.get(req.dataset_id)
    if ds is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Build a lookup: record_id -> list[Entity dict]
    golden = {rid: [Entity(**e) for e in ents] for rid, ents in req.golden_set.items()}

    # Update in-memory records
    records = uploaded_records.get(req.dataset_id, [])
    for rec in records:
        rec.final_entities = golden.get(rec.id, [])

    # Write back to the stored copy
    stored = ds.stored_path if ds.stored_path and os.path.isfile(ds.stored_path) else None
    if not stored:
        raise HTTPException(status_code=400, detail="No stored file to update")

    # Grab raw Presidio results (if available)
    presidio_results = presidio_state.get("results", {})

    if ds.format == "csv":
        buf = io.StringIO()
        # Build fieldnames: original columns + new columns
        fieldnames = list(ds.columns)
        for col in ("presidio_analyzer_entities", "final_entities"):
            if col not in fieldnames:
                fieldnames.append(col)
        writer = csv.DictWriter(buf, fieldnames=fieldnames)
        writer.writeheader()

        # Re-read original data to preserve all columns
        with open(stored, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            orig_rows = list(reader)

        for i, row in enumerate(orig_rows):
            rec_id = f"rec-{i + 1:04d}"
            # Presidio raw analysis entities
            p_ents = presidio_results.get(rec_id, [])
            row["presidio_analyzer_entities"] = json.dumps(p_ents)
            # Human-reviewed final entities
            ents = golden.get(rec_id, [])
            row["final_entities"] = json.dumps([e.model_dump() for e in ents])
            writer.writerow(row)

        with open(stored, "w", encoding="utf-8") as f:
            f.write(buf.getvalue())
    else:
        # JSON format
        with open(stored, encoding="utf-8") as f:
            data = json.load(f)

        for i, obj in enumerate(data):
            rec_id = f"rec-{i + 1:04d}"
            obj["presidio_analyzer_entities"] = presidio_results.get(rec_id, [])
            ents = golden.get(rec_id, [])
            obj["final_entities"] = [e.model_dump() for e in ents]

        with open(stored, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # Update dataset metadata
    updated_cols = list(ds.columns)
    for col in ("presidio_analyzer_entities", "final_entities"):
        if col not in updated_cols:
            updated_cols.append(col)
    _uploaded[req.dataset_id] = ds.model_copy(
        update={"has_final_entities": True, "columns": updated_cols}
    )
    _save_registry()

    return {"status": "saved", "records_updated": len(golden)}
