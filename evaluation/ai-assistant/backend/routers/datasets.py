from fastapi import APIRouter, HTTPException
from mock_data import DATASETS
from models import Dataset

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.get("", response_model=list[Dataset])
async def list_datasets():
    """List all available datasets."""
    return DATASETS


@router.get("/{dataset_id}", response_model=Dataset)
async def get_dataset(dataset_id: str):
    """Get a dataset by ID."""
    for ds in DATASETS:
        if ds.id == dataset_id:
            return ds
    raise HTTPException(status_code=404, detail="Dataset not found")
