from typing import Dict

from presidio_analyzer import AnalysisExplanation


class RecognizerResult:
    """
    Recognizer Result represents the findings of the detected entity.

    Result of a recognizer analyzing the text.

    :param entity_type: the type of the entity
    :param start: the start location of the detected entity
    :param end: the end location of the detected entity
    :param score: the score of the detection
    :param analysis_explanation: contains the explanation of why this
                                 entity was identified
    """

    def __init__(
        self,
        entity_type: str,
        start: int,
        end: int,
        score: float,
        analysis_explanation: AnalysisExplanation = None,
    ):

        self.entity_type = entity_type
        self.start = start
        self.end = end
        self.score = score
        self.analysis_explanation = analysis_explanation

    def append_analysis_explenation_text(self, text: str) -> None:
        """Add text to the analysis explanation."""
        if self.analysis_explanation:
            self.analysis_explanation.append_textual_explanation_line(text)

    def to_dict(self) -> Dict:
        """
        Serialize self to dictionary.

        :return: a dictionary
        """
        return self.__dict__

    def __str__(self) -> str:
        """Return a string representation of the instance."""
        return (
            f"type: {self.entity_type}, "
            f"start: {self.start}, "
            f"end: {self.end}, "
            f"score: {self.score}"
        )

    def __repr__(self) -> str:
        """Return a string representation of the instance."""
        return self.__str__()

    def intersects(self, other: "RecognizerResult") -> int:
        """
        Check if self intersects with a different RecognizerResult.

        :return: If intersecting, returns the number of
        intersecting characters.
        If not, returns 0
        """
        # if they do not overlap the intersection is 0
        if self.end < other.start or other.end < self.start:
            return 0

        # otherwise the intersection is min(end) - max(start)
        return min(self.end, other.end) - max(self.start, other.start)

    def contained_in(self, other: "RecognizerResult") -> bool:
        """
        Check if self is contained in a different RecognizerResult.

        :return: true if contained
        """
        return self.start >= other.start and self.end <= other.end
