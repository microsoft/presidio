import os
from typing import List, Optional
import logging
import dotenv
from presidio_analyzer import EntityRecognizer, RecognizerResult, AnalysisExplanation
from presidio_analyzer.nlp_engine import NlpArtifacts

from azure.health.deidentification import DeidentificationClient
from azure.health.deidentification.models import (
    DeidentificationContent,
    DeidentificationOperationType,
)
from azure.identity import DefaultAzureCredential

logger = logging.getLogger("presidio-streamlit")


class AHDSServiceWrapper(EntityRecognizer):
    """Wrapper for PHI detection using Azure Health Data Services De-identification."""

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        supported_language: str = "en",
        client: Optional[DeidentificationClient] = None,
        **kwargs
    ):
        """
        Wrap PHI detection using Azure Health Data Services De-identification.

        :param supported_entities: List of supported entities for this recognizer.
        :param supported_language: Language code (not used, only 'en' supported).
        :param client: Optional DeidentificationClient instance.
        :param kwargs: Additional arguments required by the parent class.
        """
        super().__init__(
            supported_entities=supported_entities,
            supported_language=supported_language,
            name="Azure Health Data Services Deidentification",
            version="1.0.0",
            **kwargs
        )

        dotenv.load_dotenv()

        endpoint = os.environ["AHDS_ENDPOINT"]
        credential = DefaultAzureCredential()
        if not client:
            client = DeidentificationClient(endpoint, credential)

        if not DeidentificationClient:
            raise ImportError(
                "Azure Health Data Services Deidentification SDK is not available. "
                "Please install azure-health-deidentification and azure-identity."
            )

        self.deid_client = client

        if not supported_entities:
            self.supported_entities = self._get_supported_entities()

    @staticmethod
    def _get_supported_entities() -> List[str]:
        # Update this list based on the latest Azure Health Data Services Deidentification documentation
        return [
        'ACCOUNT', 'AGE', 'BIOID', 'CITY', 'COUNTRY', 'DATE', 'DEVICE', 'DOCTOR',
        'EMAIL', 'HEALTHPLAN', 'HOSPITAL', 'IDNUM', 'IPADDRESS', 'LICENSE', 'LOCATION-OTHER',
        'MEDICALRECORD', 'ORGANIZATION', 'PATIENT', 'PHONE', 'PROFESSION', 'SOCIALSECURITY',
        'STATE', 'STREET', 'URL', 'USERNAME', 'VEHICLE', 'ZIP', 'FAX',
        ]

    def get_supported_entities(self) -> List[str]:
        return self.supported_entities

    def analyze(
        self, text: str, entities: List[str] = None, nlp_artifacts: NlpArtifacts = None
    ) -> List[RecognizerResult]:
        """
        Analyze text using Azure Health Data Services Deidentification (TAG operation).

        :param text: Text to analyze
        :param entities: List of entities to return (optional)
        :param nlp_artifacts: Not used
        :return: List of RecognizerResult for each PHI entity found
        """
        if not entities:
            entities = self.supported_entities

        body = DeidentificationContent(
            input_text=text,
            operation_type=DeidentificationOperationType.TAG
        )
        result = self.deid_client.deidentify_text(body)

        recognizer_results = []
        if result.tagger_result and result.tagger_result.entities:
            for entity in result.tagger_result.entities:
                category = entity.category.upper()
                if category not in [e.upper() for e in entities]:
                    continue
                analysis_explanation = AHDSServiceWrapper._build_explanation(
                    entity_type=category
                )
                recognizer_results.append(
                    RecognizerResult(
                        entity_type=category,
                        start=entity.offset.code_point,
                        end=entity.offset.code_point + entity.length.code_point,
                        score=1.0,
                        analysis_explanation=analysis_explanation,
                    )
                )
        return recognizer_results

    @staticmethod
    def _build_explanation(entity_type: str) -> AnalysisExplanation:
        explanation = AnalysisExplanation(
            recognizer=AHDSServiceWrapper.__class__.__name__,
            original_score=1.0,
            textual_explanation=f"Identified as {entity_type} by Azure Health Data Services Deidentification",
        )
        return explanation

    def load(self) -> None:
        pass


if __name__ == "__main__":
    dotenv.load_dotenv()
    text = """
    Example medical text:
    Patient: John Doe, Age: 45, Email: john.doe@example.com
    Doctor: Dr. Smith, Organization: City Hospital, Profession: Cardiologist
    Date: 2023-05-01
    """
    recognizer = AHDSServiceWrapper()
    results = recognizer.analyze(text=text)
    for res in results:
        print(res)
