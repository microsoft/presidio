from typing import Optional, List

from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

import regex as re


class DateRecognizer(PatternRecognizer):
    """
    Recognize date using regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "mm/dd/yyyy or mm/dd/yy",
            r"\b(([1-9]|0[1-9]|1[0-2])/([1-9]|0[1-9]|[1-2][0-9]|3[0-1])/(\d{4}|\d{2}))\b",  # noqa: E501
            0.6,
        ),
        Pattern(
            "dd/mm/yyyy or dd/mm/yy",
            r"\b(([1-9]|0[1-9]|[1-2][0-9]|3[0-1])/([1-9]|0[1-9]|1[0-2])/(\d{4}|\d{2}))\b",  # noqa: E501
            0.6,
        ),
        Pattern(
            "yyyy/mm/dd",
            r"\b(\d{4}/([1-9]|0[1-9]|1[0-2])/([1-9]|0[1-9]|[1-2][0-9]|3[0-1]))\b",
            0.6,
        ),
        Pattern(
            "mm-dd-yyyy",
            r"\b(([1-9]|0[1-9]|1[0-2])-([1-9]|0[1-9]|[1-2][0-9]|3[0-1])-\d{4})\b",
            0.6,
        ),
        Pattern(
            "dd-mm-yyyy",
            r"\b(([1-9]|0[1-9]|[1-2][0-9]|3[0-1])-([1-9]|0[1-9]|1[0-2])-\d{4})\b",
            0.6,
        ),
        Pattern(
            "yyyy-mm-dd",
            r"\b(\d{4}-([1-9]|0[1-9]|1[0-2])-([1-9]|0[1-9]|[1-2][0-9]|3[0-1]))\b",
            0.6,
        ),
        Pattern(
            "dd.mm.yyyy or dd.mm.yy",
            r"\b(([1-9]|0[1-9]|[1-2][0-9]|3[0-1])\.([1-9]|0[1-9]|1[0-2])\.(\d{4}|\d{2}))\b",  # noqa: E501
            0.6,
        ),
        Pattern(
            "dd-MMM-yyyy or dd-MMM-yy",
            r"\b(([1-9]|0[1-9]|[1-2][0-9]|3[0-1])-(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)-(\d{4}|\d{2}))\b",  # noqa: E501
            0.6,
        ),
        Pattern(
            "MMM-yyyy or MMM-yy",
            r"\b((JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)-(\d{4}|\d{2}))\b",  # noqa: E501
            0.6,
        ),
        Pattern(
            "dd-MMM or dd-MMM",
            r"\b(([1-9]|0[1-9]|[1-2][0-9]|3[0-1])-(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC))\b",  # noqa: E501
            0.6,
        ),
        Pattern(
            "mm/yyyy or m/yyyy",
            r"\b(([1-9]|0[1-9]|1[0-2])/\d{4})\b",
            0.2,
        ),
        Pattern(
            "mm/yy or m/yy",
            r"\b(([1-9]|0[1-9]|1[0-2])/\d{2})\b",
            0.1,
        ),
    ]

    CONTEXT = ["date", "birthday"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "DATE_TIME",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def analyze(
        self,
        text: str,
        entities: List[str],
        nlp_artifacts: NlpArtifacts = None,
        regex_flags: int = None,
    ) -> List[RecognizerResult]:
        """
        Analyzes text to detect PII using regular expressions or deny-lists.

        :param text: Text to be analyzed
        :param entities: Entities this recognizer can detect
        :param nlp_artifacts: Output values from the NLP engine
        :param regex_flags:
        :return:
        """
        regex_flags = (
            regex_flags | re.IGNORECASE
            if regex_flags
            else re.DOTALL | re.MULTILINE | re.IGNORECASE
        )  # noqa: E501

        return super().analyze(
            text=text,
            entities=entities,
            nlp_artifacts=nlp_artifacts,
            regex_flags=regex_flags,
        )
