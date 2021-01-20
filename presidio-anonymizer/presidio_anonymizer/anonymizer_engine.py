"""Handles the entire logic of the Presidio-anonymizer and text anonymizing."""
import logging

from presidio_anonymizer.entities import AnonymizerRequest


class AnonymizerEngine:
    """
    AnonymizerEngine class.

    Handles the entire logic of the Presidio-anonymizer. Gets the original text
    and replaces the PII entities with the desired transformations.
    """

    logger = logging.getLogger("presidio-anonymizer")

    def __init__(
            self,
    ):
        """Handle text replacement for PIIs with requested transformations.

        :param data: a map which contains the transformations, analyzer_results and text
        """

    def anonymize(self, engine_request: AnonymizerRequest):
        """Anonymize method to anonymize the given text.

        :return: the anonymized text
        """
        original_text = engine_request.get_text()
        last_replacement_point = len(original_text)
        output_text = engine_request.get_text()
        analyzer_results = engine_request.get_analysis_results().to_sorted_set(True)
        for analyzer_result in analyzer_results:
            transformation = engine_request.get_transformation(analyzer_result)
            self.logger.debug(f"received transformation {transformation.get('type')}")
            anonymizer_class = transformation.get("anonymizer")
            new_text = anonymizer_class().anonymize(transformation)
            end_of_text = min(analyzer_result.end, last_replacement_point)
            output_text = output_text[:analyzer_result.start] + new_text + output_text[
                                                                           end_of_text:]
            last_replacement_point = analyzer_result.start
        return output_text
