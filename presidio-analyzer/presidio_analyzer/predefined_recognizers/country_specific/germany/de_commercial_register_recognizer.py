from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class DeCommercialRegisterRecognizer(PatternRecognizer):
    """
    Recognize German Handelsregisternummer (Commercial Register number) using regex.

    German Commercial Register numbers follow these formats:
    - HRA [number] (for partnerships - Personengesellschaften)
    - HRB [number] (for corporations - Kapitalgesellschaften)
    - Optionally followed by court name

    Examples:
    - HRB 12345
    - HRA 98765 AG Munchen
    - HRB 123456 B (Berlin)

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    """

    # Pattern source: https://www.handelsregister.de/
    PATTERNS = [
        Pattern(
            "Commercial Register (HRA/HRB with number)",
            r"\b(?i)HR[AB]\s?[0-9]{1,7}(?:\s?[A-Z])?\b",
            0.4,
        ),
        Pattern(
            "Commercial Register (with court)",
            r"\b(?i)HR[AB]\s?[0-9]{1,7}(?:\s?[A-Z])?\s+(?:AG|Amtsgericht)\s+[A-Za-zäöüÄÖÜß\s]+\b",
            0.6,
        ),
        Pattern(
            "Commercial Register (full format)",
            r"\b(?i)Handelsregister\s*(?:nummer|nr\.?)?\s*:?\s*HR[AB]\s?[0-9]{1,7}\b",
            0.7,
        ),
    ]

    CONTEXT = [
        "handelsregister",
        "handelsregisternummer",
        "hr-nummer",
        "hrnr",
        "hra",
        "hrb",
        "commercial register",
        "trade register",
        "amtsgericht",
        "registergericht",
        "eingetragen",
        "firmenbuch",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_COMMERCIAL_REGISTER",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        name: Optional[str] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs if replacement_pairs else [("-", ""), (".", "")]
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
        Validate the German Commercial Register number format.

        Commercial register numbers don't have a checksum, so we validate
        the basic format only.
        """
        pattern_text = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        ).upper()

        # Must contain HRA or HRB
        if "HRA" not in pattern_text and "HRB" not in pattern_text:
            return False

        # Must contain at least one digit
        if not any(c.isdigit() for c in pattern_text):
            return False

        return None  # Return None to use pattern score
