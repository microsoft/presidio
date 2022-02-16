"""
Example implementation of a RemoteRecognizer.

Remote recognizers call external APIs
to get additional PII identification capabilities.
These results are added to all the other results
gathered by the different recognizers.

The actual call logic (e.g., HTTP or gRPC)
should be implemented within this class.
In this example, we use the `requests` package to perform a POST request.
Flow:
1. During `load`, call `supported_entities`
to get a list of what this service can detect
2. Translate the response coming from the `supported_entities` endpoint
3. During `analyze`, perform a POST request to the PII detector endpoint
4. Translate the response coming from the
PII detector endpoint into a List[RecognizerResult]
5. Return results

Note: In this example we mimic an external PII detector
by using Presidio Analyzer itself.

"""

import json
import logging
from typing import List

import requests

from presidio_analyzer import RemoteRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

logger = logging.getLogger("presidio-analyzer")


class ExampleRemoteRecognizer(RemoteRecognizer):
    """
    A reference implementation of a remote recognizer.

    Calls Presidio analyzer as if it was an external remote PII detector
    :param pii_identification_url: Service URL for detecting PII
    :param supported_entities_url: Service URL for getting the supported entities
    by this service
    """

    def __init__(
        self,
        pii_identification_url: str = "https://MYPIISERVICE_URL/detect",
        supported_entities_url: str = "https://MYPIISERVICE_URL/supported_entities",
    ):
        self.pii_identification_url = pii_identification_url
        self.supported_entities_url = supported_entities_url

        super().__init__(
            supported_entities=[], name=None, supported_language="en", version="1.0"
        )

    def load(self) -> None:
        """Call the get_supported_entities API of the external service."""
        try:
            response = requests.get(
                self.supported_entities_url,
                params={"language": self.supported_language},
            )
            self.supported_entities = self._supported_entities_from_response(response)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get supported entities from external service. {e}")
            self.supported_language = []

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        """Call an external service for PII detection."""

        payload = {"text": text, "language": self.supported_language}

        response = requests.post(
            self.pii_identification_url,
            json=payload,
            timeout=200,
        )

        results = self._recognizer_results_from_response(response)

        return results

    def get_supported_entities(self) -> List[str]:
        """Return the list of supported entities."""
        return self.supported_entities

    @staticmethod
    def _recognizer_results_from_response(
        response: requests.Response,
    ) -> List[RecognizerResult]:
        """Translate the service's response to a list of RecognizerResult."""
        results = json.loads(response.text)
        recognizer_results = [RecognizerResult(**result) for result in results]

        return recognizer_results

    @staticmethod
    def _supported_entities_from_response(response: requests.Response) -> List[str]:
        """Translate the service's supported entities list to Presidio's."""
        return json.loads(response.text)


if __name__ == "__main__":

    # Illustrative example only: Run Presidio analyzer
    # as if it was an external PII detection mechanism.
    rec = ExampleRemoteRecognizer(
        pii_identification_url="http://localhost:5002/analyze",
        supported_entities_url="http://localhost:5002/supportedentities",
    )

    remote_results = rec.analyze(
        text="My name is Morris", entities=["PERSON"], nlp_artifacts=None
    )
    print(remote_results)
