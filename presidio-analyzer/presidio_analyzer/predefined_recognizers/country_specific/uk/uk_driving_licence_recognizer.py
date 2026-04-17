import re
from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class UkDrivingLicenceRecognizer(PatternRecognizer):
    """
    Recognizes UK driving licence numbers issued by the DVLA.

    The licence number is a 16-character alphanumeric string encoding
    the holder's surname, date of birth, and initials.

    Format: SSSSS NMMDD NIIXA A
      - Positions 1-5: Surname (A-Z, padded with trailing 9s)
      - Position 6: Decade digit of birth year
      - Positions 7-8: Month of birth (01-12, or 51-62 for female)
      - Positions 9-10: Day of birth (01-31)
      - Position 11: Last digit of birth year
      - Positions 12-13: Initials (A-Z or 9 if none)
      - Position 14: Arbitrary/check digit
      - Positions 15-16: Computer check digits

    Reference: https://en.wikipedia.org/wiki/Driver%27s_license_in_the_United_Kingdom

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "UK Driving Licence",
            r"\b[A-Z9]{5}[0-9](?:0[1-9]|1[0-2]|5[1-9]|6[0-2])(?:0[1-9]|[12][0-9]|3[01])[0-9][A-Z9]{2}[A-Z0-9][A-Z]{2}\b",  # noqa: E501
            0.5,
        ),
    ]

    CONTEXT = [
        "driving licence",
        "driving license",
        "driver's licence",
        "driver's license",
        "dvla",
        "dl number",
        "licence number",
        "license number",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "UK_DRIVING_LICENCE",
        name: Optional[str] = None,
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
            name=name,
        )

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """
        Validate the pattern logic for a UK driving licence number.

        Since the DVLA check digit algorithm is not public, this method
        cannot confirm a valid licence (returns None). It can however
        reject clearly invalid patterns (returns False).

        :param pattern_text: the text to validate.
        :return: None if the pattern is plausible, False if clearly invalid.
        """
        text = pattern_text.upper()

        # Reject if surname portion is all 9s (no valid surname)
        if text[:5] == "99999":
            return False

        # Surname must have letters before any 9-padding (9s only trailing)
        surname = text[:5]
        if not re.match(r"^[A-Z]+9*$", surname):
            return False

        return None
