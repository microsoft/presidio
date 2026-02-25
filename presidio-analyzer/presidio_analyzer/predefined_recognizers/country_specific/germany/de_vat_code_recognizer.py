from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class DeVatCodeRecognizer(PatternRecognizer):
    """
    Recognize German VAT Number (Umsatzsteuer-Identifikationsnummer/USt-IdNr).

    German VAT numbers follow the format:
    - DE + 9 digits = 11 characters total
    - Example: DE123456789
    - Used for EU cross-border trade
    - No publicly documented checksum algorithm

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    """

    # Pattern source: https://ec.europa.eu/taxation_customs/vies/
    PATTERNS = [
        Pattern(
            "VAT Number (with spaces)",
            r"\bDE\s?[0-9]{3}\s?[0-9]{3}\s?[0-9]{3}\b",
            0.4,
        ),
        Pattern(
            "VAT Number (continuous)",
            r"\bDE[0-9]{9}\b",
            0.3,
        ),
    ]

    CONTEXT = [
        "umsatzsteuer-id",
        "umsatzsteuerid",
        "vat number",
        "vat id",
        "vat code",
        "steuernummer",
        "tax identification",
        "ust-id",
        "ust-id-nummer",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_VAT_CODE",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        name: Optional[str] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs
            if replacement_pairs
            else [("-", ""), (" ", ""), ("/", "")]
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
        """Validate the German VAT number format."""
        pattern_text = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        ).upper()

        if not pattern_text.startswith("DE"):
            return False

        # Correct format: DE + 9 digits = 11 characters
        if len(pattern_text) != 11:
            return False

        # Check that remaining 9 characters are digits
        if not pattern_text[2:].isdigit():
            return False

        # No publicly documented checksum algorithm for German VAT numbers
        # Return None to use pattern score with context enhancement
        return None
