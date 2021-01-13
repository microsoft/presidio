from typing import List

import tldextract

from presidio_analyzer import Pattern, PatternRecognizer


# pylint: disable=line-too-long
class EmailRecognizer(PatternRecognizer):
    """
    Recognizes email addresses using regex
    """

    PATTERNS = [
        Pattern(
            "Email (Medium)",
            r"\b((([!#$%&'*+\-/=?^_`{|}~\w])|([!#$%&'*+\-/=?^_`{|}~\w][!#$%&'*+\-/=?^_`{|}~\.\w]{0,}[!#$%&'*+\-/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)\b",  # noqa: E501
            0.5,
        ),
    ]

    CONTEXT = ["email"]

    def __init__(
        self,
        patterns: List[str] = None,
        context: List[str] = None,
        supported_language: str = "en",
        supported_entity: str = "EMAIL_ADDRESS",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text:str):
        result = tldextract.extract(pattern_text)
        return result.fqdn != ""
