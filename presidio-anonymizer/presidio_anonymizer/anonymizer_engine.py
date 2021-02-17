"""Handles the entire logic of the Presidio-anonymizer and text anonymizing."""
import logging

from presidio_anonymizer.anonymizers import Anonymizer
from presidio_anonymizer.entities import AnonymizerRequest
from presidio_anonymizer.entities import AnonymizedTextBuilder
from presidio_anonymizer.entities.anonymizer_dto import AnonymizerDTO
from presidio_anonymizer.entities.anonymizers_dto import AnonymizersDTO


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

        :return: the anonymized text
        """
        text_builder = AnonymizedTextBuilder(original_text=text)
        anonymizers = AnonymizersDTO(engine_request.get_anonymizers_dto())

        analyzer_results = (
            engine_request.get_analysis_results().to_sorted_unique_results(True)
        )

        # loop over each analyzer result
        # get AnonymizerDTO type class for the analyzer result (replace, redact etc.)
        # trigger the anonymizer method on the section of the text
        # perform the anonymization

        # concat the anonymized string into the output string
        for analyzer_result in analyzer_results:
            text_to_anonymize = text_builder.get_text_in_position(
                analyzer_result.start, analyzer_result.end)

            anonymizer_dto = anonymizers.get_anonymizer(analyzer_result.entity_type)

            self.logger.debug(
                f"for analyzer result {analyzer_result} received anonymizer "
                f"{str(anonymizer_dto)}"
            )

            anonymized_text = self.__extract_anonymizer_and_anonymize(
                analyzer_result.entity_type, anonymizer_dto,
                text_to_anonymize)
            text_builder.replace_text(anonymized_text, analyzer_result.start,
                                      analyzer_result.end)

        return text_builder.output_text

    def anonymizers(self):
        """Return a list of supported anonymizers."""
        names = [p for p in Anonymizer.get_anonymizers().keys()]
        return names

    def __extract_anonymizer_and_anonymize(self, entity_type: str,
                                           anonymizer_dto: AnonymizerDTO,
                                           text_to_anonymize: str):
        anonymizer = anonymizer_dto.anonymizer_class()
        # if the anonymizer is not valid, a InvalidParamException
        anonymizer.validate(params=anonymizer_dto.params)
        params = anonymizer_dto.params
        params["entity_type"] = entity_type
        anonymized_text = anonymizer.anonymize(
            params=params, text=text_to_anonymize
        )
        return anonymized_text
