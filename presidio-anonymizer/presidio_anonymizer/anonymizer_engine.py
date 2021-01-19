"""Handles the entire logic of the Presidio-anonymizer and text anonymizing."""
from typing import List


class AnonymizerEngine:
    """
    AnonymizerEngine class.

    Handles the entire logic of the Presidio-anonymizer. Gets the original text
    and replaces the PII entities with the desired transformations.
    """

    # Task: 2672
    # TODO this needs to be implemented currently a stab.
    # TODO replace analyze_results with domain results
    # Notice the document Omri created, it impacts the implementation
    def __init__(
            self,
            text: str,
            # TODO change to domain object
            transformations: List[str],
            # TODO change to domain object
            analyze_results: List[str],
    ):
        """
        Handle text replacement for PIIs with requested transformations.

        :param text: The original text we want to replace PIIs in
        :param transformations: The desired transformations - mapping between PII type
        and transformation type with relevant params
        :param analyze_results: The results of the analyzer of PIIs locations and scores
        """
        print("this is just a test")
        self.transformations = transformations
        self.analyze_results = analyze_results
        self.text = text
        self._end_point = len(text)

    def anonymize(self):
        """Anonymize method to anonymize the given text.

        :return: the anonymized text
        """
        # TODO a loop that goes through the analyzer results from END to START! reverse.
        # TODO for each result, replace the old value with the new value
        # Make sure we handle partial intersections using the endpoint param
        # TODO dictionary with the transformations and fields
        # To map field to its transformation
        pass
