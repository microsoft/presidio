import logging

from api.services.state.state_service import StateService

logger = logging.getLogger(__name__)

class InMemoryStateService(StateService):
    def __init__(self):
        self.store = {}

    def get_state(self, session_id):
        """Get the state for the given session_id"""

        logger.info(f"Get state for session_id: {session_id}")
        entity_mappings = self.store.get(session_id)
        if entity_mappings is None:
            logger.info(f"No state found for session_id: {session_id}")
            return None
        
        return entity_mappings

    def set_state(self, session_id, entity_mappings):
        """Set the state for the given session_id"""
        
        logger.info(f"Save state for session_id: {session_id}")
        self.store[session_id] = entity_mappings
