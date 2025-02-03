from abc import ABC, abstractmethod
from typing import List, Optional

from presidio_analyzer import EntityRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts


class RemoteRecognizer(ABC, EntityRecognizer):
    """
    A configuration for a recognizer that runs on a different process / remote machine.

    :param supported_entities: A list of entities this recognizer can identify
    :param name: name of recognizer
    :param supported_language: The language this recognizer can detect entities in
    :param version: Version of this recognizer
    """

    def __init__(
        self,
        supported_entities: List[str],
        name: Optional[str],
        supported_language: str,
        version: str,
        context: Optional[List[str]] = None,
    ):
        super().__init__(
            supported_entities=supported_entities,
            name=name,
            supported_language=supported_language,
            version=version,
            context=context,
        )

    def load(self):  # noqa D102
        pass

    @abstractmethod
    def analyze(self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts):  # noqa ANN201
        """
        Call an external service for PII detection.

        :param text: text to be analyzed
        :param entities: Entities that should be looked for
        :param nlp_artifacts: Additional metadata from the NLP engine
        :return: List of identified PII entities
        """

        # 1. Call the external service.
        # 2. Translate results into List[RecognizerResult]
        pass

    @abstractmethod
    def get_supported_entities(self) -> List[str]:  # noqa D102
        pass
