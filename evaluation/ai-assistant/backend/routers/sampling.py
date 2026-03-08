import pandas as pd
from fastapi import APIRouter, HTTPException
from models import Record, SamplingConfig, SamplingMethod
from routers.upload import _records as uploaded_records

router = APIRouter(prefix="/api/sampling", tags=["sampling"])

# Sampled records available for downstream steps
sampled_records: list[Record] = []


def _sample_random(df: pd.DataFrame, n: int) -> pd.DataFrame:
    return df.sample(n=n, random_state=42)


def _sample_length(df: pd.DataFrame, n: int) -> pd.DataFrame:
    """Stratified sampling by text length buckets (short / medium / long)."""
    lengths = df["text"].str.len()
    terciles = lengths.quantile([1 / 3, 2 / 3])
    df = df.copy()
    df["_len_bucket"] = pd.cut(
        lengths,
        bins=[-1, terciles.iloc[0], terciles.iloc[1], lengths.max() + 1],
        labels=["short", "medium", "long"],
    )
    per_bucket = max(1, n // 3)
    remainder = n - per_bucket * 3
    parts: list[pd.DataFrame] = []
    for bucket in ["short", "medium", "long"]:
        group = df[df["_len_bucket"] == bucket]
        take = min(per_bucket, len(group))
        parts.append(group.sample(n=take, random_state=42))
    collected = pd.concat(parts)
    # fill any remaining quota from the full set
    if len(collected) < n:
        remaining = df.drop(collected.index)
        extra = min(n - len(collected), len(remaining))
        if extra > 0:
            collected = pd.concat(
                [collected, remaining.sample(n=extra, random_state=42)]
            )
    return collected.drop(columns=["_len_bucket"])


_SAMPLERS = {
    SamplingMethod.random: _sample_random,
    SamplingMethod.length: _sample_length,
}


@router.post("")
async def configure_sampling(config: SamplingConfig):
    """Sample records from the loaded dataset."""
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
    sampler = _SAMPLERS[config.method]
    sampled_df = sampler(df, sample_size)
    sampled_records = [
        Record(**row) for row in sampled_df.to_dict(orient="records")
    ]

    return {
        "sample_size": len(sampled_records),
        "total_records": total,
        "method": config.method.value,
        "status": "ready",
    }


@router.get("/records")
async def get_sampled_records():
    """Return the current set of sampled records."""
    return sampled_records
