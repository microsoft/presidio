from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class DeLicensePlateRecognizer(PatternRecognizer):
    """
    Recognize German license plate (Kennzeichen) using regex.

    German license plates follow the standard EU format:
    - Structure: [District Code]-[Recognition Letters] [Digits][Suffix]
    - District codes (Unterscheidungszeichen): 1-3 letters representing the city/region
    - Recognition letters (Erkennungsnummer): 1-2 letters (REQUIRED for standard plates)
    - Digits: 1-4 numbers (cannot start with 0)
    - Suffix: Optional E (electric/hybrid) or H (historic "Oldtimer" 30+ years)
    - Maximum 8 characters total (excluding hyphen/spaces)

    Examples:
    - B-AB 1234 (Berlin, standard)
    - M-XY 123E (Munich, electric vehicle)
    - HH-OL 99H (Hamburg, historic vehicle)

    Special plate formats NOT covered by this recognizer:
    - Government/authority plates without recognition letters (e.g., "B 1234")
      These are rare and reserved for Behördenfahrzeuge (official vehicles).
    - Diplomatic plates (0-XXX-YYY format)
    - Military plates (Y-XXXXX format)
    - Seasonal plates (with validity period)

    Source: https://www.kba.de/DE/Service/Kennzeichen/kennzeichen_node.html

    Parameters
    ----------
    patterns : List[Pattern], optional
        List of patterns to be used by this recognizer
    context : List[str], optional
        List of context words to increase confidence in detection
    supported_language : str
        Language this recognizer supports (default: "de")
    supported_entity : str
        The entity this recognizer can detect (default: "DE_LICENSE_PLATE")
    replacement_pairs : List[Tuple[str, str]], optional
        List of tuples with potential replacement values
    """

    # Pattern source: https://www.kba.de/DE/Service/Kennzeichen/kennzeichen_node.html
    PATTERNS = [
        Pattern(
            "License Plate (hyphen format with E/H suffix)",
            r"\b[A-ZÄÖÜ]{1,3}-[A-Z]{1,2}\s?[1-9][0-9]{0,3}[EH]?\b",
            0.5,
        ),
        Pattern(
            "License Plate (space format with E/H suffix)",
            r"\b[A-ZÄÖÜ]{1,3}\s[A-Z]{1,2}\s[1-9][0-9]{0,3}[EH]?\b",
            0.4,
        ),
        Pattern(
            "License Plate (continuous format)",
            r"\b[A-ZÄÖÜ]{1,3}[A-Z]{1,2}[1-9][0-9]{0,3}[EH]?\b",
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
        """
        Validate the German license plate format.

        Checks:
        - Length constraints (5-8 characters excluding separators)
        - Valid character set (letters, digits, umlauts, E/H suffix)
        - Structure: must have letters followed by digits (with optional E/H)
        """
        pattern_text = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        ).upper()

        # Handle E/H suffix for electric/historic vehicles
        suffix = ""
        if pattern_text and pattern_text[-1] in ("E", "H"):
            # Check if it's actually a suffix (preceded by digit)
            if len(pattern_text) > 1 and pattern_text[-2].isdigit():
                suffix = pattern_text[-1]
                pattern_text = pattern_text[:-1]

        # Length check: 5-8 characters (excluding separators, including suffix)
        total_len = len(pattern_text) + len(suffix)
        if total_len < 5 or total_len > 8:
            return False

        # Must contain both letters and digits
        has_letters = any(c.isalpha() for c in pattern_text)
        has_digits = any(c.isdigit() for c in pattern_text)
        if not (has_letters and has_digits):
            return False

        # Allow umlauts in district codes (e.g., Tübingen = TÜ)
        valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ÄÖÜ")
        if not all(c in valid_chars for c in pattern_text):
            return False

        return None  # Use pattern score
