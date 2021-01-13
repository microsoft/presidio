from typing import List

from presidio_analyzer import EntityRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts


class RemoteRecognizer(EntityRecognizer):
    """
    A configuration for a recognizer that runs on a different process
     / remote machine
    """

    def __init__(
        self,
        supported_entities: List[str],
        name: str,
        supported_language: str,
        version: str,
    ):
        super().__init__(supported_entities, name, supported_language, version)

    def load(self):
        pass

    def analyze(self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts):
        # add code here to connect to the side car
        pass

    def get_supported_entities(self):
        pass
