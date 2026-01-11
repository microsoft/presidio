from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class DePostalCodeRecognizer(PatternRecognizer):
    """
    Recognize German Postleitzahl (Postal Code) using regex.

    German postal codes are 5 digits (01000 - 99999).
    Geographic regions use specific ranges, but regex validation is flexible.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    """

    # Pattern source: https://www.deutschepost.de/
    PATTERNS = [
        Pattern(
            "Postal Code (5 digits)",
            r"\b[0-9]{5}\b",
            0.3,
        ),
    ]

    CONTEXT = [
        "postleitzahl",
        "plz",
        "postal code",
        "post code",
        "zip code",
        "postcode",
        "ort",
        "stadt",
    ]

    # Valid postal code ranges per German region (approximate)
    # This is a simplified list; actual ranges are more complex
    VALID_RANGES = {
        "BW": (70000, 79999),  # Baden-Württemberg
        "BY": (80000, 87999),  # Bavaria
        "BE": (10000, 14999),  # Berlin
        "BB": (14500, 19999),  # Brandenburg
        "HB": (28000, 28999),  # Bremen
        "HH": (20000, 21999),  # Hamburg
        "HE": (60000, 65999),  # Hesse
        "MV": (17000, 18999),  # Mecklenburg-Vorpommern
        "NI": (20000, 49999),  # Lower Saxony
        "NW": (40000, 59999),  # North Rhine-Westphalia
        "RP": (50000, 57999),  # Rhineland-Palatinate
        "SL": (66000, 66999),  # Saarland
        "SN": (1000, 9999),    # Saxony (includes leading zero)
        "ST": (6000, 39999),   # Saxony-Anhalt
        "SH": (22000, 25999),  # Schleswig-Holstein
        "TH": (97000, 99999),  # Thuringia
    }

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_POSTAL_CODE",
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
        """Validate the German postal code format."""
        pattern_text = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        )

        if len(pattern_text) != 5:
            return False

        if not pattern_text.isdigit():
            return False

        # Check if in valid range (01000 - 99999)
        postal_code = int(pattern_text)
        if postal_code < 1000 or postal_code > 99999:
            return False

        return None  # Return None to use pattern score (no definitive validation)
