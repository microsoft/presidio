"""Handles the entire logic of the Presidio-anonymizer and text anonymizing."""
import logging
from typing import List, Dict, Optional

from presidio_anonymizer.anonymizers import Anonymizer
from presidio_anonymizer.entities import AnalyzerResult, \
    AnalyzerResults
from presidio_anonymizer.entities import AnonymizedTextBuilder
from presidio_anonymizer.entities.anonymizer_config import AnonymizerConfig

DEFAULT = "replace"


class AnonymizerEngine:
    """
    AnonymizerEngine class.

    Handles the entire logic of the Presidio-anonymizer. Gets the original text
    and replaces the PII entities with the desired anonymizers.
    """

    def __init__(self):
        self.logger = logging.getLogger("presidio-anonymizer")

    def anonymize(self, text: str, analyzer_results: List[AnalyzerResult],
                  anonymizers_config: Optional[
                      Dict[str, AnonymizerConfig]] = None) -> str:
        """Anonymize method to anonymize the given text.

        :param text: the text we are anonymizing
        :param analyzer_results: A list of AnalyzerResult class -> The results we
        received from the analyzer
        :param anonymizers_config: The configuration of the anonymizers we would like
        to use for each entity e.g.: {"PHONE_NUMBER":AnonymizerConfig("redact", {})}
        received from the analyzer
        :return: the anonymized text
        """
        text_builder = AnonymizedTextBuilder(original_text=text)
        if not anonymizers_config:
            anonymizers_config = {}

        analyzer_results = (
            AnalyzerResults(analyzer_results).to_sorted_unique_results(True)
        )

        # loop over each analyzer result
        # get AnonymizerConfig for the analyzer result
        # trigger the anonymize method on the section of the text
        # perform the anonymization
        # concat the anonymized string into the output string
        for analyzer_result in analyzer_results:
            text_to_anonymize = text_builder.get_text_in_position(
                analyzer_result.start, analyzer_result.end)

            anonymizer_config = self.__get_anonymizer_config_by_entity_type(
                analyzer_result.entity_type,
                anonymizers_config)

            self.logger.debug(
                f"for analyzer result {analyzer_result} received config "
                f"{anonymizer_config}"
            )

            anonymized_text = self.__extract_anonymizer_and_anonymize(
                analyzer_result.entity_type, anonymizer_config,
                text_to_anonymize)
            text_builder.replace_text(anonymized_text, analyzer_result.start,
                                      analyzer_result.end)

        return text_builder.output_text

    @staticmethod
    def get_anonymizers() -> List[str]:
        """Return a list of supported anonymizers."""
        names = [p for p in Anonymizer.get_anonymizers().keys()]
        return names

    def __extract_anonymizer_and_anonymize(self, entity_type: str,
                                           anonymizer_config: AnonymizerConfig,
                                           text_to_anonymize: str) -> str:
        self.logger.debug(f"getting anonymizer for {entity_type}")
        anonymizer = anonymizer_config.anonymizer_class()
        self.logger.debug(
            f"validating anonymizer {anonymizer} for {entity_type}")
        anonymizer.validate(params=anonymizer_config.params)
        params = anonymizer_config.params
        params["entity_type"] = entity_type
        self.logger.debug(
            f"anonymizing {entity_type} with {anonymizer}")
        anonymized_text = anonymizer.anonymize(
            params=params, text=text_to_anonymize
        )
        return anonymized_text

    @staticmethod
    def __get_anonymizer_config_by_entity_type(
            entity_type: str,
            anonymizers_config: Dict[str, AnonymizerConfig]) -> AnonymizerConfig:
        # We try to get the anonymizer from the list by entity_type.
        # If it does not exist, we try to get the default from the list.
        # If there is no default we fallback into the current DEFAULT which is replace.
        anonymizer = anonymizers_config.get(entity_type)
        if not anonymizer:
            anonymizer = anonymizers_config.get("DEFAULT")
            if not anonymizer:
                anonymizer = AnonymizerConfig(DEFAULT, {})
        return anonymizer
