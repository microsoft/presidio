from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class DeLicensePlateRecognizer(PatternRecognizer):
    """
    Recognize German license plate (Kennzeichen) using regex.

    German license plates follow the format:
    - Standard EU format: [District Code] [1-2 Letters] [1-4 Numbers]
      Example: B-AB 1234 (Berlin) or M-XY 123 (Munich)
    - District codes: 1-3 letters representing the region
    - Up to 8 characters total (excluding separators)

    Format: [1-3 letters district][space/dash]?[1-2 letters][space/dash]?[1-4 numbers]

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    """

    # Pattern source: https://www.kba.de/DE/Service/Kennzeichen/kennzeichen_node.html
    PATTERNS = [
        Pattern(
            "License Plate (EU format with separators)",
            r"\b[A-Z]{1,3}[-\s][A-Z]{1,2}[-\s][1-9][0-9]{0,3}\b",
            0.5,
        ),
        Pattern(
            "License Plate (mixed separators)",
            r"\b[A-Z]{1,3}[-\s]?[A-Z]{1,2}[-\s]?[1-9][0-9]{0,3}\b",
            0.3,
        ),
        Pattern(
            "License Plate (continuous)",
            r"\b[A-Z]{1,3}[A-Z]{1,2}[1-9][0-9]{0,3}\b",
            0.3,
        ),
    ]

    CONTEXT = [
        "kennzeichen",
        "license plate",
        "number plate",
        "registration plate",
        "fahrzeugkennzeichen",
        "fahrzeug",
        "auto",
        "kfz",
        "fahrzeugregistrierung",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_LICENSE_PLATE",
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
        """Validate the German license plate format."""
        pattern_text = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        ).upper()

        if len(pattern_text) < 5 or len(pattern_text) > 9:
            return False

        # Must contain letters and numbers
        has_letters = any(c.isalpha() for c in pattern_text)
        has_digits = any(c.isdigit() for c in pattern_text)

        if not (has_letters and has_digits):
            return False

        # Valid special character: ß (oldtimer)
        if any(c in "äöüß" for c in pattern_text.lower()):
            return True  # Special case for oldtimer plates

        # Standard validation: only letters and digits allowed
        if not all(c.isalnum() for c in pattern_text):
            return False

        return None  # Use pattern score
