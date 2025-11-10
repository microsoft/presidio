from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from presidio_analyzer import RemoteRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts


class LMRecognizer(RemoteRecognizer, ABC):
    """
    Abstract base class for PII detection using Language Models (LLMs, SLMs, etc.).
    
    Provides common functionality for language model-based recognizers including:
    - Model configuration management
    - Temperature and scoring controls
    - Common prompt handling patterns
    """

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        supported_language: str = "en",
        name: str = "Language Model PII Recognizer",
        version: str = "1.0.0",
        model_id: Optional[str] = None,
        temperature: Optional[float] = None,
        min_score: float = 0.5,
        **kwargs
    ):
        """
        Initialize language model recognizer base class.

        :param supported_entities: List of PII entities to detect.
        :param supported_language: Language code (default 'en').
        :param name: Recognizer name.
        :param version: Recognizer version.
        :param model_id: Language model identifier.
        :param temperature: Model temperature for generation.
        :param min_score: Minimum confidence score for results.
        :param kwargs: Additional arguments for parent class.
        """
        super().__init__(
            supported_entities=supported_entities or [],
            supported_language=supported_language,
            name=name,
            version=version,
            **kwargs
        )
        
        self.model_id = model_id
        self.temperature = temperature
        self.min_score = min_score

    @abstractmethod
    def _call_llm(
        self,
        text: str,
        prompt: str,
        **kwargs
    ) -> str:
        """
        Make a call to the LLM service.
        
        :param text: Text to analyze.
        :param prompt: Prompt to send to the LLM.
        :param kwargs: Additional parameters specific to the LLM provider.
        :return: Raw response from the LLM.
        """
        ...

    @abstractmethod
    def _parse_llm_response(
        self,
        response: str,
        original_text: str
    ) -> List:
        """
        Parse the LLM response into structured data.
        
        :param response: Raw response from the LLM.
        :param original_text: Original text that was analyzed.
        :return: List of extracted entities in LLM-specific format.
        """
        ...

    @abstractmethod
    def _validate_llm_availability(self) -> bool:
        """
        Check if the LLM service is available and accessible.
        
        :return: True if the LLM service is available, False otherwise.
        """
        ...

    @abstractmethod
    def _calculate_confidence_score(self, extraction_info: Dict) -> float:
        """
        Calculate confidence score for an extraction.
        
        Must be implemented by subclasses for specific scoring logic.
        
        :param extraction_info: Information about the extraction.
        :return: Confidence score between 0 and 1.
        """
        ...

    def get_supported_entities(self) -> List[str]:
        """Return list of supported PII entity types."""
        return self.supported_entities
