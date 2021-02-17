"""Handles the entire logic of the Presidio-anonymizer and text anonymizing."""
import logging

from presidio_anonymizer.anonymizers import Anonymizer
from presidio_anonymizer.entities import AnonymizerRequest
from presidio_anonymizer.entities import AnonymizedTextBuilder
from presidio_anonymizer.entities.anonymizer_config import AnonymizerConfig


class AnonymizerEngine:
    """
    AnonymizerEngine class.

    Handles the entire logic of the Presidio-anonymizer. Gets the original text
    and replaces the PII entities with the desired anonymizers.
    """

    logger = logging.getLogger("presidio-anonymizer")

    def __init__(
            self,
    ):
        """Handle text replacement for PIIs with requested anonymizers.

        :param data: a map which contains the anonymizers, analyzer_results and text
        """

    def anonymize(self, text: str, engine_request: AnonymizerRequest) -> str:
        """Anonymize method to anonymize the given text.

        :param text: the text we are anonymizing
        :param engine_request: DEPRECATED ABOUT OT BE REMOVED.
        :return: the anonymized text
        """
        text_builder = AnonymizedTextBuilder(original_text=text)

        analyzer_results = (
            engine_request.get_analysis_results().to_sorted_unique_results(True)
        )

        # loop over each analyzer result
        # get AnonymizerConfig type class for the analyzer result (replace, redact etc.)
        # trigger the anonymizer method on the section of the text
        # perform the anonymization

        # concat the anonymized string into the output string
        for analyzer_result in analyzer_results:
            text_to_anonymize = text_builder.get_text_in_position(
                analyzer_result.start, analyzer_result.end)

            anonymizer_config = self.get_anonymizer(
                engine_request.get_anonymizers_config(),
                analyzer_result.entity_type)

            self.logger.debug(
                f"for analyzer result {analyzer_result} received anonymizer "
                f"{str(anonymizer_config)}"
            )

            anonymized_text = self.__extract_anonymizer_and_anonymize(
                analyzer_result.entity_type, anonymizer_config,
                text_to_anonymize)
            text_builder.replace_text(anonymized_text, analyzer_result.start,
                                      analyzer_result.end)

        return text_builder.output_text

    def anonymizers(self):
        """Return a list of supported anonymizers."""
        names = [p for p in Anonymizer.get_anonymizers().keys()]
        return names

    def __extract_anonymizer_and_anonymize(self, entity_type: str,
                                           anonymizer_config: AnonymizerConfig,
                                           text_to_anonymize: str):
        anonymizer = anonymizer_config.anonymizer_class()
        # if the anonymizer is not valid, a InvalidParamException
        anonymizer.validate(params=anonymizer_config.params)
        params = anonymizer_config.params
        params["entity_type"] = entity_type
        anonymized_text = anonymizer.anonymize(
            params=params, text=text_to_anonymize
        )
        return anonymized_text

    @staticmethod
    def get_anonymizer(anonymizers: dict, entity_type: str):
        """
        Get the right anonymizer from the list.

        When anonymizer does not exist, we fall back to default.
        :param entity_type: the type of the text we want to do anonymizer over
        :return: anonymizer
        """
        anonymizer = anonymizers.get(entity_type)
        if not anonymizer:
            anonymizer = anonymizers.get("DEFAULT")
            if not anonymizer:
                anonymizer = AnonymizerConfig("replace", {})
        return anonymizer
