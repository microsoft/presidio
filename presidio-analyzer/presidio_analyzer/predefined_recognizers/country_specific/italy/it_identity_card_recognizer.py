from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer

# An Identity Card is a personal recognition document that is valid in Italy.
# The paper-based identity card was issued for nearly 87 years until 2018
# and can still be issued in case of emergency. The Electronic Identity Card
# (CIE) is progressively replacing the paper-based identity card. It is
# issued upon expiration of the paper-based identity card or in case of loss,
# theft or deterioration.
#
# References:
# - https://en.wikipedia.org/wiki/Italian_electronic_identity_card
# - https://www.cartaidentita.interno.gov.it/en/cie/electronic-identity-card


class ItIdentityCardRecognizer(PatternRecognizer):
    """
    Recognizes Italian Identity Card number using case-insensitive regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Paper-based Identity Card (very weak)",
            # The number is composed of 2 letters, space (optional), 7 digits
            r"(?i)\b[A-Z]{2}\s?\d{7}\b",  # noqa: E501
            0.01,
        ),
        Pattern(
            "Electronic Identity Card (CIE) 2.0 (very weak)",
            r"(?i)\b\d{7}[A-Z]{2}\b",  # noqa: E501
            0.01,
        ),
        Pattern(
            "Electronic Identity Card (CIE) 3.0 (very weak)",
            r"(?i)\b[A-Z]{2}\d{5}[A-Z]{2}\b",  # noqa: E501
            0.01,
        ),
    ]

    CONTEXT = [
        "carta",
        "identità",
        "elettronica",
        "cie",
        "documento",
        "riconoscimento",
        "espatrio",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "it",
        supported_entity: str = "IT_IDENTITY_CARD",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
