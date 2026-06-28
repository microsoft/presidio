import logging
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, Optional

from services.presidio.python_presidio_service import PythonPresidioService
from services.presidio.hybrid_presidio_service import HybridPresidioService
from services.presidio.http_presidio_service import HttpPresidioService
from services.toolkit_service import ToolkitService
from services.state.redis_state_service import RedisStateService

app = FastAPI()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AnonymizeRequest(BaseModel):
    text: str
    session_id: Optional[str] = None
    language: Optional[str] = "en"


class AnonymizeResponse(BaseModel):
    session_id: str
    text: str


class DeanonymizeRequest(BaseModel):
    text: str
    session_id: str


class DeanonymizeResponse(BaseModel):
    text: str


presidio_service = PythonPresidioService()
# presidio_service = HttpPresidioService()
# presidio_service = HybridPresidioService()
state_service = RedisStateService()
toolkit_service = ToolkitService(presidio_service, state_service)

def get_toolkit_service() -> ToolkitService:
    return toolkit_service


@app.post("/anonymize", response_model=AnonymizeResponse)
async def anonymize_endpoint(
    request: AnonymizeRequest,
    toolkit_service: ToolkitService = Depends(get_toolkit_service)
) -> Any:
    """Anonymize the given text using Toolkit service"""

    logger.info(f"Anonymize endpoint called with session_id: '{request.session_id}'")

    try:
        result = toolkit_service.anonymize(
            text=request.text, session_id=request.session_id, language=request.language
        )
        return result
    except Exception as e:
        logger.exception(f"Error during anonymization: {e}")
        raise HTTPException(
            status_code=500, detail="An error occurred during anonymization"
        )

@app.post("/deanonymize", response_model=DeanonymizeResponse)
async def deanonymize_endpoint(
    request: DeanonymizeRequest,
    toolkit_service: ToolkitService = Depends(get_toolkit_service)
):
    """Deanonymize the given text using Toolkit service"""

    logger.info(f"Deanonymize endpoint called with session_id: '{request.session_id}'")

    try:
        result = toolkit_service.deanonymize(text=request.text, session_id=request.session_id)
        return result
    except ValueError as ve:
        logger.error(f"Deanonymization value error: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.exception(f"Error during deanonymization: {e}")
        raise HTTPException(
            status_code=500, detail="An error occurred during deanonymization"
        )
