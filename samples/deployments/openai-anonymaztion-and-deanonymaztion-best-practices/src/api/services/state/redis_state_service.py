import json
import logging
from presidio_anonymizer import OperatorResult
import redis

from services.state.state_service import StateService
from config.config import config

logger = logging.getLogger(__name__)


class RedisStateService(StateService):
    def __init__(self):
        self.redis = redis.Redis(
            host=config.Redis.hostname,
            port=config.Redis.port,
            db=0,
            password=config.Redis.key,
            ssl=config.Redis.ssl)

    def get_state(self, session_id):
        """Get the state for the given session_id"""

        logger.info(f"Get state for session_id: {session_id}")
        json_data = self.redis.get(session_id)
        if json_data is None:
            logger.info(f"No state found for session_id: {session_id}")
            return None
        
        entity_mappings = json.loads(json_data) 
        return entity_mappings

    def set_state(self, session_id, entity_mappings):
        """Set the state for the given session_id"""

        logger.info(f"Seve state for session_id: {session_id}")
        self.redis.set(session_id, json.dumps(entity_mappings))
