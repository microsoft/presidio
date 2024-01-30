from presidio_analyzer import Pattern
from typing import Optional, Callable
from regex import Match
from .analysis_explanation import AnalysisExplanation


class ImprovablePattern(Pattern):
    """
    A class that represents a regex pattern.

    :param name: the name of the pattern
    :param regex: the regex pattern to detect
    :param score: the pattern's strength (values varies 0-1)
    :param get_improved_pattern_func: a function that improve the score of the analysis explanation
    based on the regex match info.
    Can be used when is needed to improve the score based on detected groups in the regex match
    or any logic applied only to this pattern.
    """

    def __init__(
        self,
        name: str,
        regex: str,
        score: float,
        improve_score_fn: Optional[
            Callable[["ImprovablePattern", str, Match, AnalysisExplanation], None]
        ] = None,
    ) -> None:

        super().__init__(name, regex, score)
        self.improve_score_fn = improve_score_fn

    def improve_score(
        self, matched_text: str, match: Match, analysis_explanation: AnalysisExplanation
    ) -> None:
        if self.improve_score_fn:
            self.improve_score_fn(self, matched_text, match, analysis_explanation)
