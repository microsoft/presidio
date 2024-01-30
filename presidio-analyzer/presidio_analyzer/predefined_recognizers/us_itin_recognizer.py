from typing import Optional, List
from presidio_analyzer import (
    AnalysisExplanation,
    ImprovablePatternRecognizer,
    ImprovablePattern,
)

from regex import Match


def improve_itin_pattern(
    pattern: ImprovablePattern, matched_text: str, match: Match, analysis_explanation: AnalysisExplanation
):
    """
    Change the score of the itin by checking if contains '-' or ' ' characters as separators.
    """
    first_separator = match.group(1)
    second_separator = match.group(2)

    if first_separator and second_separator:
        return

    if not first_separator and not second_separator:
        analysis_explanation.pattern_name = "Itin (weak)"
        analysis_explanation.set_improved_score(0.3)
        analysis_explanation.append_textual_explanation_line(
            "Weak pattern. No separators"
        )
        return

    analysis_explanation.pattern_name = "Itin (very weak)"
    analysis_explanation.set_improved_score(0.05)
    analysis_explanation.append_textual_explanation_line(
        "Very Weak pattern. Only one separator"
    )


class UsItinRecognizer(ImprovablePatternRecognizer):
    """
    Recognizes US ITIN (Individual Taxpayer Identification Number) using regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        ImprovablePattern(
            "Itin (medium)",
            r"\b9\d{2}([- ]?)(?:5\d|6[0-5]|7\d|8[0-8]|9(?:[0-2]|[4-9]))([- ]?)\d{4}\b",
            0.5,
            improve_itin_pattern,
        ),
    ]

    CONTEXT = ["individual", "taxpayer", "itin", "tax", "payer", "taxid", "tin"]

    def __init__(
        self,
        patterns: Optional[List[ImprovablePattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "US_ITIN",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
