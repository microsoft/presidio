from fastapi import APIRouter

from models import SamplingConfig

router = APIRouter(prefix="/api/sampling", tags=["sampling"])


@router.post("")
async def configure_sampling(config: SamplingConfig):
    """Accept sampling configuration and return a summary."""
    return {
        "sample_size": config.sample_size,
        "method": "stratified_random",
        "status": "ready",
    }
