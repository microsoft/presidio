"""
An example implementation of a TextAnalyticsRecognizer.

Calls an existing Azure Text Analytics instance
to get additional PII identification capabilities.

Needs setting up a Text Analytics resource as a prerequisite:
https://github.com/MicrosoftDocs/azure-docs/blob/master/articles/cognitive-services/text-analytics/includes/create-text-analytics-resource.md
"""

from dataclasses import dataclass
from typing import List, Dict

import requests
import yaml

from presidio_analyzer import (
    RecognizerResult,
    RemoteRecognizer,
    AnalysisExplanation,
)
from presidio_analyzer.nlp_engine import NlpArtifacts


@dataclass
class TextAnalyticsEntityCategory:
    """
    A Category recognized by Text Analytics 'Named entity recognition and PII'.

    The full list can be found here:
    https://docs.microsoft.com/en-us/azure/cognitive-services/text-analytics/named-entity-types?tabs=personal#category-datetime
    """

    name: str
    entity_type: str
    supported_languages: List[str]
    subcategory: str = None


class TextAnalyticsClient:
    """Client for Microsoft Text Analytics."""

    CATEGORY = "category"
    SUBCATEGORY = "subcategory"
    OFFSET = "offset"
    LENGTH = "length"
    CONFIDENCE_SCORE = "confidenceScore"

    def __init__(
        self,
        key: str,
        endpoint: str,
    ):
        """
        Call pii recognition endpoint, and holds DTO constants.

        :param text_analytics_key: The key used to authenticate to Text Analytics Azure
            Instance.
        :param text_analytics_endpoint: Supported Cognitive Services or Text Analytics
            resource endpoints (protocol and hostname).
        """
        self.key = key
        self.endpoint = endpoint

    def recognize_pii_entities(self, text: str, language: str) -> List[Dict]:
        """
        Return identified PII entities from Text Analytics.

        :param text: The text for analysis.
        :param language: The text language.
        :return: List of PII entities recognized by Text Analytics
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Ocp-Apim-Subscription-Key": self.key,
        }
        data = {"documents": [{"id": 1, "language": language, "text": text}]}
        pii_recognition_path = (
            "/text/analytics/v3.1/entities/recognition/pii?domain=phi"
        )
        response = requests.post(
            self.endpoint + pii_recognition_path, json=data, headers=headers
        )
        return response.json()["documents"][0]["entities"]


class TextAnalyticsRecognizer(RemoteRecognizer):
    """
    Recognize PII entities using a remote Text Analytics Server.

    Using an existing instance of Text Analytics, this recognizer detects multiple
     PIIs from a fixed list,
    https://docs.microsoft.com/en-us/azure/cognitive-services/text-analytics/named-entity-types?tabs=personal
    and replaces their types to align with Presidio's.

    :param supported_language: Language this recognizer supports
    :param text_analytics_key: The key used to authenticate to Text Analytics Azure
        instance.
    :param text_analytics_endpoint: Supported Cognitive Services or Text Analytics
        resource endpoints (protocol and hostname).
    :param text_analytics_categories: The categories supported by this recognizer,
        their supported_languages and their corresponding Presidio entity type.
        If not passed, will be loaded with the values in the file with path
        'text_analytics_categories_file_location' parameter.
    :param categories_file_location: The location for the yaml file
        with the text text_analytics_categories supported by this recognizer.
    """

    def __init__(
        self,
        text_analytics_key: str,
        text_analytics_endpoint: str,
        supported_language: str = "en",
        text_analytics_categories: List[TextAnalyticsEntityCategory] = None,
        categories_file_location: str = None,
    ):
        self.supported_language = supported_language
        self.text_analytics_client = TextAnalyticsClient(
            text_analytics_key, text_analytics_endpoint
        )
        self.text_analytics_categories = text_analytics_categories
        if not self.text_analytics_categories:
            self.text_analytics_categories = self._get_conf_file_categories(
                categories_file_location
            )

        super().__init__(
            supported_entities=self.get_supported_entities(),
            supported_language=supported_language,
            name="Text Analytics",
            version="3.1",
        )

    def load(self):  # noqa D102
        pass

    def get_supported_entities(self) -> List[str]:
        """
        Text Analytics Supported Entities.

        :return: List of the supported entities matching the Text Analytics categories'
         supported_languages.
        """
        return [
            category.entity_type
            for category in self.text_analytics_categories
            if self.supported_language in category.supported_languages
        ]

    def analyze(
        self, text: str, entities: List[str] = [], nlp_artifacts: NlpArtifacts = None
    ) -> List[RecognizerResult]:
        """
        Analyze text using Text Analytics.

        :param text: The text for analysis.
        :param entities: Not used by this recognizer.
        :param nlp_artifacts: Not used by this recognizer.
        :return: The list of Presidio RecognizerResult constructed from the recognized
            Text Analytics detections.
        """
        text_analytics_entities = self.text_analytics_client.recognize_pii_entities(
            text, language=self.supported_language
        )
        category_names = [category.name for category in self.text_analytics_categories]
        return [
            self._convert_to_recognizer_result(categorized_entity)
            for categorized_entity in text_analytics_entities
            if categorized_entity["category"] in category_names
        ]

    def _convert_to_recognizer_result(
        self, categorized_entity: Dict
    ) -> RecognizerResult:
        entity_type = self._get_presidio_entity_type(categorized_entity)

        return RecognizerResult(
            entity_type=entity_type,
            start=categorized_entity[TextAnalyticsClient.OFFSET],
            end=categorized_entity[TextAnalyticsClient.OFFSET]
            + categorized_entity[TextAnalyticsClient.LENGTH],
            score=categorized_entity[TextAnalyticsClient.CONFIDENCE_SCORE],
            analysis_explanation=TextAnalyticsRecognizer._build_explanation(
                original_score=categorized_entity[TextAnalyticsClient.CONFIDENCE_SCORE],
                entity_type=entity_type,
            ),
        )

    def _get_presidio_entity_type(self, categorized_entity: Dict) -> str:
        if categorized_entity.get(TextAnalyticsClient.SUBCATEGORY):
            entity_type = next(
                filter(
                    lambda x: categorized_entity[TextAnalyticsClient.SUBCATEGORY]
                    == x.subcategory
                    and categorized_entity[TextAnalyticsClient.CATEGORY] == x.name,
                    self.text_analytics_categories,
                )
            ).entity_type
        else:
            entity_type = next(
                filter(
                    lambda x: categorized_entity[TextAnalyticsClient.CATEGORY]
                    == x.name,
                    self.text_analytics_categories,
                )
            ).entity_type
        return entity_type

    @staticmethod
    def _build_explanation(
        original_score: float, entity_type: str
    ) -> AnalysisExplanation:
        explanation = AnalysisExplanation(
            recognizer=TextAnalyticsRecognizer.__class__.__name__,
            original_score=original_score,
            textual_explanation=f"Identified as {entity_type} by Text Analytics",
        )
        return explanation

    @staticmethod
    def _get_conf_file_categories(file_location):
        """Load the Presidio-supported TextAnalyticsEntityCategory from a yaml configuration file."""  # noqa E501
        categories_file = yaml.safe_load(open(file_location))
        return [TextAnalyticsEntityCategory(**category) for category in categories_file]


if __name__ == "__main__":
    import os
    from presidio_analyzer import AnalyzerEngine

    # Instruction for setting up Text Analytics and fetch instance key and endpoint:
    # https://github.com/MicrosoftDocs/azure-docs/blob/master/articles/cognitive-services/text-analytics/includes/create-text-analytics-resource.md # noqa E501
    text_analytics_recognizer = TextAnalyticsRecognizer(
        text_analytics_key="<YOUR_TEXT_ANALYTICS_KEY>",
        text_analytics_endpoint="<YOUR_TEXT_ANALYTICS_ENDPOINT>",
        categories_file_location=os.path.join(
            os.path.dirname(__file__), "example_text_analytics_entity_categories.yaml"
        ),
    )

    analyzer = AnalyzerEngine()
    analyzer.registry.add_recognizer(text_analytics_recognizer)
    results = analyzer.analyze(
        text="David is 30 years old. His IBAN: IL150120690000003111111", language="en"
    )
    print(results)
