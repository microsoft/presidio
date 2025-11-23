import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from presidio_analyzer import RecognizerResult, RemoteRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts

logger = logging.getLogger("presidio-analyzer")

GENERIC_PII_ENTITY = "GENERIC_PII_ENTITY"


class LMRecognizer(RemoteRecognizer, ABC):
    """
    Base class for language model-based PII recognizers.

    Provides common functionality for LLM-based entity detection.
    Subclasses implement _call_llm() for specific LLM providers.
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
        labels_to_ignore: Optional[List[str]] = None,
        enable_generic_consolidation: bool = True,
        **kwargs
    ):
        """Initialize LM recognizer.

        :param supported_entities: Entity types to detect.
        :param labels_to_ignore: Entity labels to skip.
        :param enable_generic_consolidation: Consolidate unknown
            entities to GENERIC_PII_ENTITY.
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
        self.labels_to_ignore = [label.lower() for label in (labels_to_ignore or [])]
        self.enable_generic_consolidation = enable_generic_consolidation

        self._generic_entities_logged = set()

        if (
            self.enable_generic_consolidation
            and GENERIC_PII_ENTITY not in self.supported_entities
        ):
            self.supported_entities.append(GENERIC_PII_ENTITY)

    @abstractmethod
    def _call_llm(
        self,
        text: str,
        entities: List[str],
        **kwargs
    ) -> List[RecognizerResult]:
        """
        Call LLM service and return RecognizerResult objects.

        Subclasses implement this to integrate with specific LLM providers.

        :param text: Text to analyze for PII.
        :param entities: Entity types to detect.
        :return: List of RecognizerResult objects.
        """
        ...

    def analyze(
        self,
        text: str,
        entities: Optional[List[str]] = None,
        nlp_artifacts: Optional[NlpArtifacts] = None
    ) -> List[RecognizerResult]:
        """Analyze text for PII/PHI using LLM."""
        if not text or not text.strip():
            logger.debug("Empty text provided, returning empty results")
            return []

        if entities is None:
            requested_entities = self.supported_entities
        else:
            requested_entities = [e for e in entities if e in self.supported_entities]

        if not requested_entities:
            logger.debug(
                "No requested entities (%s) match supported entities (%s)",
                entities, self.supported_entities
            )
            return []

        try:
            results = self._call_llm(text, requested_entities)

            filtered_results = self._filter_and_process_results(
                results, requested_entities
            )

            if filtered_results:
                logger.info(
                    "LLM recognizer found %d PII entities",
                    len(filtered_results),
                )

            return filtered_results

        except Exception as e:
            logger.exception("LLM analysis failed for %s", self.name)
            return []

    def _filter_and_process_results(
        self,
        results: List[RecognizerResult],
        requested_entities: Optional[List[str]] = None
    ) -> List[RecognizerResult]:
        """Filter and process RecognizerResult objects from LLM."""
        filtered_results = []

        for result in results:
            if not result.entity_type:
                logger.warning("LLM returned result without entity_type, skipping")
                continue

            if result.entity_type.lower() in self.labels_to_ignore:
                logger.debug(
                    "Entity %s at [%d:%d] is in labels_to_ignore, skipping",
                    result.entity_type, result.start, result.end
                )
                continue

            original_entity_type = result.entity_type
            if result.entity_type not in self.supported_entities:
                if self.enable_generic_consolidation:
                    result.entity_type = GENERIC_PII_ENTITY

                    if original_entity_type not in self._generic_entities_logged:
                        logger.warning(
                            "Detected unmapped entity '%s', "
                            "consolidated to GENERIC_PII_ENTITY. "
                            "To map or exclude, update "
                            "'entity_mappings' or 'labels_to_ignore'.",
                            original_entity_type,
                        )
                        self._generic_entities_logged.add(original_entity_type)

                    if result.recognition_metadata is None:
                        result.recognition_metadata = {}
                    result.recognition_metadata[
                        "original_entity_type"
                    ] = original_entity_type
                else:
                    logger.warning(
                        "Detected unmapped entity '%s', skipped "
                        "(enable_generic_consolidation=False). "
                        "To map or exclude, update "
                        "'entity_mappings' or 'labels_to_ignore'.",
                        result.entity_type,
                    )
                    continue

            if requested_entities and result.entity_type not in requested_entities:
                logger.debug(
                    "Entity %s at [%d:%d] not in requested entities %s, skipping",
                    result.entity_type, result.start, result.end, requested_entities
                )
                continue

            if result.start is None or result.end is None:
                logger.warning(
                    "LLM returned result without start/end positions, skipping"
                )
                continue

            if result.score < self.min_score:
                logger.debug(
                    "Entity %s at [%d:%d] below min_score (%.2f < %.2f), skipping",
                    result.entity_type, result.start, result.end,
                    result.score, self.min_score
                )
                continue

            filtered_results.append(result)

        return filtered_results

    def get_supported_entities(self) -> List[str]:
        """Return list of supported PII entity types."""
        return self.supported_entities
