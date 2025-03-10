from abc import ABC, abstractmethod
from typing import List, Tuple

from presidio_anonymizer import OperatorResult


class PresidioService(ABC):
    @abstractmethod
    def anonymize_text(self, session_id: str, text: str, language: str, entity_mappings: dict) -> Tuple[str, dict]:
        pass
    
    @abstractmethod
    def deanonymize_text(self, session_id: str, text: str, entity_mappings: dict) -> str:
        pass
