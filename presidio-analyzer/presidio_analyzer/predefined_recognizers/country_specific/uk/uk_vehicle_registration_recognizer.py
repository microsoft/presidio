from typing import List, Optional, Tuple

from presidio_analyzer import Pattern, PatternRecognizer
from presidio_analyzer.entity_recognizer import EntityRecognizer


class UkVehicleRegistrationRecognizer(PatternRecognizer):
    """
    Recognizes UK vehicle registration numbers using regex.

    Supports three formats still commonly seen on the road:

    - Current (2001+): 2 area letters + 2-digit age id + 3 random letters
      e.g. AB51 ABC
    - Prefix (1983-2001): year letter + 1-3 digits + 3 letters
      e.g. A123 BCD
    - Suffix (1963-1983): 3 letters + 1-3 digits + year letter
      e.g. ABC 123D

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples for replacing characters in the
        pattern text for validation
    """

    PATTERNS = [
        Pattern(
            "UK Vehicle Registration (current)",
            r"\b[A-HJ-PR-Y][A-HJ-PR-Y](?:0[1-9]|[1-7][0-9])[- ]?[A-HJ-PR-Z]{3}\b",
            0.3,
        ),
        Pattern(
            "UK Vehicle Registration (prefix)",
            r"\b[A-HJ-NPR-TV-Y]\d{1,3}[- ]?[A-HJ-PR-Y][A-HJ-PR-Z]{2}\b",
            0.2,
        ),
        Pattern(
            "UK Vehicle Registration (suffix)",
            r"\b[A-HJ-PR-Z]{3}[- ]?\d{1,3}[- ]?[A-HJ-NPR-TV-Y]\b",
            0.15,
        ),
    ]

    CONTEXT = [
        "vehicle",
        "registration",
        "number plate",
        "licence plate",
        "license plate",
        "reg",
        "vrn",
        "dvla",
        "v5c",
        "logbook",
        "mot",
        "car",
        "insured vehicle",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "UK_VEHICLE_REGISTRATION",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        name: Optional[str] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs if replacement_pairs else [("-", ""), (" ", "")]
        )
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
        Validate the matched pattern.

        Only the current format (2001+) is validated further by checking
        that the two-digit age identifier falls in a valid range:
        02-29 (March registrations) or 51-79 (September registrations).

        Prefix and suffix formats return None (keep base score).

        :param pattern_text: The matched text to validate
        :return: True if valid current format, False if invalid current
            format, None for prefix/suffix formats
        """
        sanitized_value = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        )

        # Current format is exactly 7 chars after sanitization
        if len(sanitized_value) == 7 and sanitized_value[:2].isalpha():
            age_id_str = sanitized_value[2:4]
            if age_id_str.isdigit():
                age_id = int(age_id_str)
                return (2 <= age_id <= 29) or (51 <= age_id <= 79)

        return None
