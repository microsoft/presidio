"""Handles the entire logic of the Presidio-anonymizer and text anonymizing."""
from presidio_anonymizer.entities import AnonymizerEngineRequest


class AnonymizerEngine:
    """
    AnonymizerEngine class.

    Handles the entire logic of the Presidio-anonymizer. Gets the original text
    and replaces the PII entities with the desired transformations.
    """

    # Task: 2672
    # TODO this needs to be implemented currently a stab.
    # TODO replace analyze_results with entities results
    # Notice the document Omri created, it impacts the implementation
    def __init__(
            self,
    ):
        """Handle text replacement for PIIs with requested transformations.

        :param data: a map which contains the transformations, analyzer_results and text
        """

    def anonymize(self, engine_request: AnonymizerEngineRequest):
        """Anonymize method to anonymize the given text.

        :return: the anonymized text
        """
        # TODO a loop that goes through the analyzer results from END to START! reverse.
        # TODO for each result, replace the old value with the new value
        # Make sure we handle partial intersections using the endpoint param
        # TODO dictionary with the transformations and fields
        # To map field to its transformation
        return ""
