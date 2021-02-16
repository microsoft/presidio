"""Handles the entire logic of the Presidio-anonymizer and text anonymizing."""
import logging

from presidio_anonymizer.anonymizers import Anonymizer
from presidio_anonymizer.entities import AnonymizerRequest
from presidio_anonymizer.entities import TextBuilder


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
        text_manipulator = TextBuilder(original_text=engine_request.get_text())

        analyzer_results = (
            engine_request.get_analysis_results().to_sorted_unique_results(True)
        )

        # loop over each analyzer result
        # get anonymizer type class for the analyzer result (replace, redact etc.)
        # trigger the anonymizer method on the section of the text
        # perform the anonymization

        # concat the anonymized string into the output string
        for analyzer_result in analyzer_results:
            text_to_anonymize = text_manipulator.get_text_in_position(
                analyzer_result.start, analyzer_result.end)

            transformation = engine_request.get_transformation(
                analyzer_result.entity_type
            )
            self.logger.debug(
                f"for analyzer result {analyzer_result} received transformation "
                f"{str(transformation)}"
            )

            anonymized_text = self.__extract_anonymizer_and_anonymize(transformation,
                                                                      text_to_anonymize)

            text_manipulator.replace_text(anonymized_text, analyzer_result.start,
                                          analyzer_result.end)

        return text_manipulator.output_text

    def anonymizers(self):
        """Return a list of supported anonymizers."""
        names = [p for p in self.builtin_anonymizers.keys()]
        return names

    def __extract_anonymizer_and_anonymize(self, transformation, text_to_anonymize):
        anonymizer = transformation.get("anonymizer")()
        # if the anonymizer is not valid, a InvalidParamException
        anonymizer.validate(params=transformation)
        anonymized_text = anonymizer.anonymize(
            params=transformation, text=text_to_anonymize
        )
        return anonymized_text
