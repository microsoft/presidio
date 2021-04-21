import logging
import os
from pathlib import Path
from typing import List

import yaml

from presidio_analyzer import (
    RecognizerResult,
    RemoteRecognizer,
    AnalysisExplanation,
)
from presidio_analyzer.nlp_engine import NlpArtifacts
from presidio_analyzer.text_analytics_entity_category import TextAnalyticsEntityCategory
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

logger = logging.getLogger("presidio-analyzer")


class TextAnalyticsRecognizer(RemoteRecognizer):
    """
    Recognize PII entities using a remote Text Analytics Server.

    Using an existing instance of Text Analytics, this recognizer recognizes multiple
     PIIs from a fixed list,
    https://docs.microsoft.com/en-us/azure/cognitive-services/text-analytics/named-entity-types?tabs=personal
    and replaces their types to align with Presidio's.

    :param supported_language: Language this recognizer supports
    :param text_analytics_key: The key used to authenticate to Text Analytics Azure
        Instance. If not passed will be evaluated from the TEXT_ANALYTICS_KEY
        environment variable, where its existence will determine the if this
        recognizer is enabled.
    :param text_analytics_endpoint: Supported Cognitive Services or Text Analytics
        resource endpoints (protocol and hostname). If not passed will be evaluated
        from the TEXT_ANALYTICS_ENDPOINT environment variable, where its existence
        will determine if this recognizer is enabled.
    :param text_analytics_categories: The categories supported by this recognizers,
        their languages and their corresponding Presidio entity type. If not passed,
        will be loaded with the default list in 'text_analytics_entity_categories.yaml'
        file.
    """

    def __init__(
        self,
        supported_language: str = "en",
        text_analytics_key: str = os.environ.get("TEXT_ANALYTICS_KEY"),
        text_analytics_endpoint: str = os.environ.get("TEXT_ANALYTICS_ENDPOINT"),
        text_analytics_categories: List[TextAnalyticsEntityCategory] = None,
    ):
        self.supported_language = supported_language
        self.text_analytics_key = text_analytics_key
        self.text_analytics_endpoint = text_analytics_endpoint
        self.text_analytics_categories = text_analytics_categories
        self.text_analytics_client = None
        self.enabled = (
            self.text_analytics_key and self.text_analytics_endpoint
        ) is not None
        if self.enabled and not self.text_analytics_categories:
            self.text_analytics_categories = self._get_default_categories()

        super().__init__(
            supported_entities=self.get_supported_entities(),
            supported_language=supported_language,
            name="Text Analytics",
            version="3.1",
        )

    def load(self):
        """
        Initialize the recognizer's Text Analytics Client.

        If the recognizer is enabled (passed with Text Analytics key and endpoint).

        """
        if self.enabled:
            logger.info("Loading Text Analytics Recognizer")
            credential = AzureKeyCredential(self.text_analytics_key)
            self.text_analytics_client = TextAnalyticsClient(
                endpoint=self.text_analytics_endpoint, credential=credential
            )

    def get_supported_entities(self) -> List[str]:
        """
        Text Analytics Supported Entities.

        :return: List of the supported entities matching the Text Analytics categories'
         languages.
        """
        return (
            [
                category.entity_type
                for category in self.text_analytics_categories
                if self.supported_language in category.languages
            ]
            if self.enabled
            else []
        )

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts = None
    ) -> List[RecognizerResult]:
        """
        Analyze text using Text Analytics.

        :param text: The text for analysis.
        :param entities: Not used by this recognizer.
        :param nlp_artifacts: Not used by this recognizer.
        :return: The list of Presidio RecognizerResult constructed from the recognized
            Text Analytics detections.
        """
        if self.enabled:
            result = self.text_analytics_client.recognize_pii_entities(
                [text], language="en"
            )
            category_names = [
                category.name for category in self.text_analytics_categories
            ]
            return [
                self._convert_to_recognizer_result(categorized_entity)
                for categorized_entity in result[0].entities
                if categorized_entity.category in category_names
            ]

    def _convert_to_recognizer_result(self, categorized_entity):
        if categorized_entity.subcategory:
            entity_type = next(
                filter(
                    lambda x: categorized_entity.subcategory == x.subcategory
                    and categorized_entity.category == x.name,
                    self.text_analytics_categories,
                )
            ).entity_type
        else:
            entity_type = next(
                filter(
                    lambda x: categorized_entity.category == x.name,
                    self.text_analytics_categories,
                )
            ).entity_type

        return RecognizerResult(
            entity_type=entity_type,
            start=categorized_entity.offset,
            end=categorized_entity.offset + len(categorized_entity.text),
            score=categorized_entity.confidence_score,
            analysis_explanation=TextAnalyticsRecognizer._build_explanation(
                original_score=categorized_entity.confidence_score,
                entity_type=entity_type,
            ),
        )

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
    def _get_default_categories():
        file_location = Path(
            Path(__file__).parent.parent.parent,
            "conf",
            "text_analytics_entity_categories.yaml",
        )
        categories_file = yaml.safe_load(open(file_location))
        return [TextAnalyticsEntityCategory(**category) for category in categories_file]
