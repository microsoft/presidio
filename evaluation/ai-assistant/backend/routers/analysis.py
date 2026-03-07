import asyncio

from fastapi import APIRouter

from mock_data import RECORDS
from models import AnalysisStatus, Record

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

# In-memory state for the current analysis run
_state: dict = {
    "presidio_progress": 0,
    "llm_progress": 0,
    "running": False,
}


@router.post("/start")
async def start_analysis():
    """Kick off parallel Presidio + LLM analysis (simulated)."""
    _state["presidio_progress"] = 0
    _state["llm_progress"] = 0
    _state["running"] = True

    async def _simulate():
        while _state["presidio_progress"] < 100 or _state["llm_progress"] < 100:
            if _state["presidio_progress"] < 100:
                _state["presidio_progress"] = min(100, _state["presidio_progress"] + 4)
            if _state["llm_progress"] < 100:
                _state["llm_progress"] = min(100, _state["llm_progress"] + 3)
            await asyncio.sleep(0.2)
        _state["running"] = False

    asyncio.create_task(_simulate())
    return {"status": "started"}


@router.get("/status", response_model=AnalysisStatus)
async def get_analysis_status():
    presidio_done = _state["presidio_progress"] >= 100
    llm_done = _state["llm_progress"] >= 100

    result = AnalysisStatus(
        presidio_progress=_state["presidio_progress"],
        llm_progress=_state["llm_progress"],
        presidio_complete=presidio_done,
        llm_complete=llm_done,
    )

    if presidio_done:
        result.presidio_stats = {
            "records": 500,
            "entities": 1247,
            "types": 12,
            "avg_confidence": 91,
        }
    if llm_done:
        result.llm_stats = {
            "records": 500,
            "entities": 1312,
            "additional": 65,
            "avg_confidence": 87,
        }
    if presidio_done and llm_done:
        result.comparison = {
            "matches": 1182,
            "conflicts": 47,
            "llm_only": 65,
            "presidio_only": 18,
        }
    return result


@router.get("/records", response_model=list[Record])
async def get_records():
    """Return all records with their detected entities."""
    return RECORDS


@router.get("/records/{record_id}", response_model=Record)
async def get_record(record_id: str):
    for rec in RECORDS:
        if rec.id == record_id:
            return rec
    return {"error": "not found"}
