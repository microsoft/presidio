from fastapi import APIRouter
from mock_data import RECORDS
from models import Entity, EntityAction, Record

router = APIRouter(prefix="/api/review", tags=["review"])

# In-memory golden set: record_id -> confirmed entities
_golden_set: dict[str, list[Entity]] = {}
_reviewed: set[str] = set()


@router.get("/records", response_model=list[Record])
async def get_review_records():
    """List records for human review."""
    return RECORDS


@router.post("/records/{record_id}/confirm")
async def confirm_entity(record_id: str, action: EntityAction):
    """Confirm an entity and add it to the golden set."""
    _golden_set.setdefault(record_id, []).append(action.entity)
    _reviewed.add(record_id)
    return {"status": "confirmed", "record_id": record_id}


@router.post("/records/{record_id}/reject")
async def reject_entity(record_id: str, action: EntityAction):
    """Reject an entity and remove it from the golden set."""
    entities = _golden_set.get(record_id, [])
    _golden_set[record_id] = [
        e
        for e in entities
        if not (
            e.text == action.entity.text
            and e.start == action.entity.start
            and e.end == action.entity.end
        )
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
    total = len(RECORDS)
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
