"""Handles the entire logic of the Presidio-anonymizer and text anonymizing."""
import logging

from presidio_anonymizer.anonymizers import Anonymizer
from presidio_anonymizer.entities import AnonymizerRequest, InvalidParamException


class AnonymizerEngine:
    """
    AnonymizerEngine class.

    Handles the entire logic of the Presidio-anonymizer. Gets the original text
    and replaces the PII entities with the desired transformations.
    """

    logger = logging.getLogger("presidio-anonymizer")
    builtin_anonymizers = {
        cls.anonymizer_name(cls): cls for cls in Anonymizer.__subclasses__()
    }

    def __init__(
        self,
    ):
        """Handle text replacement for PIIs with requested transformations.

        :param data: a map which contains the transformations, analyzer_results and text
        """

    def anonymize(self, engine_request: AnonymizerRequest) -> str:
        """Anonymize method to anonymize the given text.

        :return: the anonymized text
        """
        original_full_text = engine_request.get_text()
        text_len = len(original_full_text)
        last_replacement_point = text_len
        output_text = original_full_text
        analyzer_results = (
            engine_request.get_analysis_results().to_sorted_unique_results(True)
        )

        # loop over each analyzer result
        # get anonymizer type class for the analyzer result (replace, redact etc.)
        # trigger the anonymizer method on the section of the text
        # perform the anonymization
        # concat the anonymized string into the output string
        for analyzer_result in analyzer_results:
            self.__validate_position_over_text(analyzer_result, text_len)

            transformation = engine_request.get_transformation(
                analyzer_result.entity_type
            )
            self.logger.debug(
                f"for analyzer result {analyzer_result} received transformation "
                f"{str(transformation)}"
            )

            anonymizer = self.__extract_anonymizer(transformation)

            anonymized_text = self.__anonymize_section(
                anonymizer, output_text, analyzer_result, transformation
            )

            output_text = self.__update_output_with_anonymized_section(
                analyzer_result, last_replacement_point, output_text, anonymized_text
            )

            last_replacement_point = analyzer_result.start
        return output_text

    def anonymizers(self):
        """Return a list of supported anonymizers."""
        names = [p for p in self.builtin_anonymizers.keys()]
        return names

    def __validate_position_over_text(self, analyzer_result, text_len):
        if text_len < analyzer_result.start or analyzer_result.end > text_len:
            raise InvalidParamException(
                f"Invalid analyzer result: '{analyzer_result}', "
                f"original text length is only {text_len}."
            )

    def __extract_anonymizer(self, transformation):
        anonymizer = transformation.get("anonymizer")()
        # if the anonymizer is not valid, a InvalidParamException
        anonymizer.validate(params=transformation)
        return anonymizer

    def __anonymize_section(
        self, anonymizer, output_text, analyzer_result, transformation
    ):
        text_to_anonymize = output_text[analyzer_result.start : analyzer_result.end]
        anonymized_text = anonymizer.anonymize(
            params=transformation, text=text_to_anonymize
        )
        return anonymized_text

    def __update_output_with_anonymized_section(
        self, analyzer_result, last_replacement_point, output_text, anonymized_text
    ):
        end_of_text = min(analyzer_result.end, last_replacement_point)
        return (
            output_text[: analyzer_result.start]
            + anonymized_text
            + output_text[end_of_text:]
        )
