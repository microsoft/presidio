"""Handles the entire logic of the Presidio-anonymizer and text anonymizing."""
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
            data: dict,
    ):
        """
               Handle text replacement for PIIs with requested transformations.

               :param text: The original text we want to replace PIIs in
               :param transformations: The desired transformations - mapping between PII type
               and transformation type with relevant params
               :param analyze_results: The results of the analyzer of PIIs locations and scores
               """
        self._transformations = data.get("transformations")
        self._analyze_results = data.get("analyzer_results")
        self._text = data.get("text")
        self._end_point = len(self._text)

    def anonymize(self):
        """Anonymize method to anonymize the given text.

        :return: the anonymized text
        """
        # TODO a loop that goes through the analyzer results from END to START! reverse.
        # TODO for each result, replace the old value with the new value
        # Make sure we handle partial intersections using the endpoint param
        # TODO dictionary with the transformations and fields
        # To map field to its transformation
        return ""
