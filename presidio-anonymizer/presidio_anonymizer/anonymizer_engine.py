"""Handles the entire logic of the Presidio-anonymizer and text anonymizing."""
import logging

from presidio_anonymizer.anonymizers import Anonymizer
from presidio_anonymizer.entities import AnonymizerRequest
from presidio_anonymizer.entities import AnonymizedTextBuilder


class AnonymizerEngine:
    """
    AnonymizerEngine class.

    Handles the entire logic of the Presidio-anonymizer. Gets the original text
    and replaces the PII entities with the desired anonymizers.
    """

    logger = logging.getLogger("presidio-anonymizer")
    builtin_anonymizers = {
        cls.anonymizer_name(cls): cls for cls in Anonymizer.__subclasses__()
    }

    def __init__(
            self,
    ):
        """Handle text replacement for PIIs with requested anonymizers.

        :param data: a map which contains the anonymizers, analyzer_results and text
        """

    def anonymize(self, engine_request: AnonymizerRequest) -> str:
        """Anonymize method to anonymize the given text.

        :return: the anonymized text
        """
        text_builder = AnonymizedTextBuilder(original_text=engine_request.get_text())

        analyzer_results = (
            engine_request.get_analysis_results().to_sorted_unique_results(True)
        )

        # loop over each analyzer result
        # get anonymizer type class for the analyzer result (replace, redact etc.)
        # trigger the anonymizer method on the section of the text
        # perform the anonymization

        # concat the anonymized string into the output string
        for analyzer_result in analyzer_results:
            text_to_anonymize = text_builder.get_text_in_position(
                analyzer_result.start, analyzer_result.end)

            anonymizer_dto = engine_request.get_anonymizer_dto(
                analyzer_result.entity_type
            )
            self.logger.debug(
                f"for analyzer result {analyzer_result} received anonymizer "
                f"{str(anonymizer_dto)}"
            )

            anonymized_text = self.__extract_anonymizer_and_anonymize(anonymizer_dto,
                                                                      text_to_anonymize)
            text_builder.replace_text(anonymized_text, analyzer_result.start,
                                      analyzer_result.end)

        return text_builder.output_text

    def anonymizers(self):
        """Return a list of supported anonymizers."""
        names = [p for p in self.builtin_anonymizers.keys()]
        return names

    def __extract_anonymizer_and_anonymize(self, anonymizer_dto, text_to_anonymize):
        anonymizer = anonymizer_dto.get("anonymizer")()
        # if the anonymizer is not valid, a InvalidParamException
        anonymizer.validate(params=anonymizer_dto)
        anonymized_text = anonymizer.anonymize(
            params=anonymizer_dto, text=text_to_anonymize
        )
        return anonymized_text
