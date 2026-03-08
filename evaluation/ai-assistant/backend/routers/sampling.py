import pandas as pd
from fastapi import APIRouter, HTTPException
from models import Record, SamplingConfig
from routers.upload import _records as uploaded_records

router = APIRouter(prefix="/api/sampling", tags=["sampling"])

# Sampled records available for downstream steps
sampled_records: list[Record] = []


@router.post("")
async def configure_sampling(config: SamplingConfig):
    """Sample records from the loaded dataset using pandas."""
    global sampled_records

    records = uploaded_records.get(config.dataset_id)
    if not records:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset '{config.dataset_id}' not found.",
        )

    total = len(records)
    sample_size = min(config.sample_size, total)

    if sample_size <= 0:
        raise HTTPException(
            status_code=400,
            detail="Sample size must be greater than 0.",
        )

    df = pd.DataFrame([r.model_dump() for r in records])
    sampled_df = df.sample(n=sample_size, random_state=42)
    sampled_records = [
        Record(**row) for row in sampled_df.to_dict(orient="records")
    ]

    return {
        "sample_size": sample_size,
        "total_records": total,
        "method": "random",
        "status": "ready",
    }


@router.get("/records")
async def get_sampled_records():
    """Return the current set of sampled records."""
    return sampled_records
