from typing import List, Optional
from presidio_analyzer import (
    AnalysisExplanation,
    EntityRecognizer,
    ImprovablePatternRecognizer,
    ImprovablePattern,
)
from presidio_analyzer.string_sanitizers import StringSanitizer, TranslateSanitizer
from regex import Match


def improve_ssn_pattern(
    pattern: ImprovablePattern, matched_text: str, match: Match, analysis_explanation: AnalysisExplanation
):
    """
    Change the score of the ssn by checking if contains separator characters.
    """
    first_separator = match.group(1)
    second_separator = match.group(2)
    analysis_explanation.set_improved_score(0.05)

    if first_separator and second_separator:
        if first_separator != second_separator:
            analysis_explanation.set_improved_score(EntityRecognizer.MIN_SCORE)
        else:
            analysis_explanation.set_improved_score(pattern.score)
    elif not first_separator and not second_separator:
        analysis_explanation.pattern_name = "SSN4 (very weak)"
    elif first_separator:
        if first_separator == "-":
            analysis_explanation.pattern_name = "SSN2 (very weak)"
        else:
            analysis_explanation.set_improved_score(EntityRecognizer.MIN_SCORE)
    else:
        if second_separator == "-":
            analysis_explanation.pattern_name = "SSN1 (very weak)"
        else:
            analysis_explanation.set_improved_score(EntityRecognizer.MIN_SCORE)


class UsSsnRecognizer(ImprovablePatternRecognizer):
    """Recognize US Social Security Number (SSN) using regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        ImprovablePattern(
            "SSN5 (medium)",
            r"\b[0-9]{3}([\.\- ])?[0-9]{2}([\.\- ])?[0-9]{4}\b",
            0.5,
            improve_ssn_pattern,
        )
    ]

    CONTEXT = [
        "social",
        "security",
        # "sec", # Task #603: Support keyphrases ("social sec")
        "ssn",
        "ssns",
        "ssn#",
        "ss#",
        "ssid",
    ]

    def __init__(
        self,
        patterns: Optional[List[ImprovablePatternRecognizer]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "US_SSN",
        sanitizer: Optional[StringSanitizer] = None,
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
        self.sanitizer = sanitizer or TranslateSanitizer({".": "", "-": "", " ": ""})

    def improve_score(
        self,
        pattern: ImprovablePattern,
        matched_text: str,
        match: Match,
        analysis_explanation: AnalysisExplanation,
    ):
        sanitized_value = self.sanitizer.sanitize(matched_text)
        if self.is_invalid_ssn(sanitized_value):
            analysis_explanation.set_improved_score(EntityRecognizer.MIN_SCORE)

    def is_invalid_ssn(self, only_digits: str) -> bool:
        if all(only_digits[0] == c for c in only_digits):
            # cannot be all same digit
            return True

        if only_digits[3:5] == "00" or only_digits[5:] == "0000":
            # groups cannot be all zeros
            return True

        for sample_ssn in ("000", "666", "123456789", "98765432", "078051120"):
            if only_digits.startswith(sample_ssn):
                return True

        return False
