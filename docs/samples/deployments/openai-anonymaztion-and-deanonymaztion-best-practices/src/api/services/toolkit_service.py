import logging
import uuid
from typing import Optional

from services.state.state_service import StateService
from services.presidio.presidio_service import PresidioService

logger = logging.getLogger(__name__)


class ToolkitService:
    def __init__(self, presidio_service: PresidioService, state_service: StateService):
        self.presidio_service = presidio_service
        self.state_service = state_service

    def anonymize(self, text: str, session_id: Optional[str] = None, language: Optional[str] = "en") -> dict:
        """Anonymize the given text using Presidio service"""

        entity_mappings = None
        if not session_id:
            logger.info(f"Anonymize called without session_id")
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session_id: {session_id}")
        else:
            logger.info(f"Anonymize called with session_id: {session_id}")
            entity_mappings = self.state_service.get_state(session_id)

        try:
            anonymized_text, new_entity_mappings = self.presidio_service.anonymize_text(
                session_id, text, language, entity_mappings
            )
            
            # Save the state in the state service
            self.state_service.set_state(session_id, new_entity_mappings)

            return {"session_id": session_id, "text": anonymized_text}
        except Exception as e:
            logger.exception(f"Error during anonymization for session_id {session_id} {e}")
            raise e


    def deanonymize(self, text: str, session_id: str) -> dict:
        """Deanonymize the given text using Presidio service"""

        logger.info(f"Deanonymize endpoint called with session_id: {session_id}")

        entity_mappings = self.state_service.get_state(session_id)
        if entity_mappings is None:
            raise ValueError("Deanonymization is not possible because the session is not found")

        try:
            deanonymized_text = self.presidio_service.deanonymize_text(
                session_id, text, entity_mappings
            )
            return {"text": deanonymized_text}
        except Exception as e:
            logger.exception(f"Error during deanonymization for session_id {session_id}  {e}")
            raise e
