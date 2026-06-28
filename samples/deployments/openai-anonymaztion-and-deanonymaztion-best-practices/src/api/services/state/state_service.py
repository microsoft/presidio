from abc import ABC, abstractmethod


class StateService(ABC):
    @abstractmethod
    def get_state(self, session_id):
        pass
    
    @abstractmethod
    def set_state(self, session_id, entity_mappings):
        pass
