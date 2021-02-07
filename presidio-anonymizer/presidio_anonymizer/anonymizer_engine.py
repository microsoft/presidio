"""Handles the entire logic of the Presidio-anonymizer and text anonymizing."""
import logging

from presidio_anonymizer.anonymizers import Mask, FPE, Replace, Hash, Redact
from presidio_anonymizer.entities import AnonymizerRequest, InvalidParamException


class AnonymizerEngine:
    """
    AnonymizerEngine class.

    Handles the entire logic of the Presidio-anonymizer. Gets the original text
    and replaces the PII entities with the desired transformations.
    """

    logger = logging.getLogger("presidio-anonymizer")
    builtin_anonymizers = {
        "mask": Mask,
        "fpe": FPE,
        "replace": Replace,
        "hash": Hash,
        "redact": Redact,
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
        for analyzer_result in analyzer_results:
            transformation = engine_request.get_transformation(analyzer_result)
            self.logger.debug(
                f"for analyzer result {analyzer_result} received transformation "
                f"{str(transformation)}"
            )
            self.__validate_position_over_text(analyzer_result, text_len)
            anonymizer = transformation.get("anonymizer")()
            anonymizer.validate(params=transformation)
            text_to_anonymize = output_text[analyzer_result.start : analyzer_result.end]
            anonymized_text = anonymizer.anonymize(
                params=transformation, text=text_to_anonymize
            )  # TODO: [ADO-2754] replace with the singleton class instance
            end_of_text = min(analyzer_result.end, last_replacement_point)
            output_text = (
                output_text[: analyzer_result.start]
                + anonymized_text
                + output_text[end_of_text:]
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
