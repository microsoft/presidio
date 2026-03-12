from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class DeDriverLicenseRecognizer(PatternRecognizer):
    """
    Recognize German Fuhrerscheinnummer (Driver's License number) using regex.

    German driver's license numbers vary by issuing authority and time period:
    - EU card format (since 2013): Alphanumeric, typically 11 characters
    - Older formats vary by state (Bundesland)

    The format is generally: [Authority code][Serial number][Check digit]

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    """

    # Pattern source: https://www.kba.de/EN/Themen_en/ZentraleRegister_en/ZFER_en/FE_Klassen_en/Muster_en/muster_node_en.html
    PATTERNS = [
        Pattern(
            "Driver License (EU format)",
            r"\b[A-Z0-9]{2,4}[0-9]{6,7}[A-Z0-9]{0,2}\b",
            0.1,
        ),
        Pattern(
            "Driver License (alphanumeric)",
            r"\b[A-Z]{1}[0-9]{2}[A-Z0-9]{8}\b",
            0.15,
        ),
    ]

    CONTEXT = [
        "fuhrerschein",
        "führerschein",
        "fuhrerscheinnummer",
        "führerscheinnummer",
        "driver license",
        "driving license",
        "fahrerlaubnis",
        "führerschein-nr",
        "fs-nr",
        "fahrerlaubnisnummer",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_DRIVER_LICENSE",
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
        Validate the German driver's license number format.

        Since German driver's license numbers don't have a standardized
        checksum algorithm across all formats, we perform basic format validation.
        """
        pattern_text = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        ).upper()

        # Basic length validation (German DL numbers are typically 10-11 chars)
        if len(pattern_text) < 8 or len(pattern_text) > 15:
            return False

        # Must contain both letters and numbers
        has_letters = any(c.isalpha() for c in pattern_text)
        has_digits = any(c.isdigit() for c in pattern_text)

        if not (has_letters and has_digits):
            return False

        return None  # Return None to use pattern score (no definitive validation)
