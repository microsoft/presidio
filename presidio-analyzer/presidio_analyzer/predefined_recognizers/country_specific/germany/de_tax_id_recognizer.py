from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class DeTaxIdRecognizer(PatternRecognizer):
    """
    Recognizes German Tax Identification Numbers (Steueridentifikationsnummer).

    The Steueridentifikationsnummer (Steuer-IdNr) is an 11-digit tax
    identification number assigned to every person registered in Germany.
    It uses an ISO 7064 MOD 11,10 check digit and has an occurrence rule:
    exactly one digit must appear exactly twice (or three times),
    and one digit must not appear at all (or appear once fewer).

    Reference: https://de.wikipedia.org/wiki/Steuerliche_Identifikationsnummer

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    for different strings to be used during pattern matching.
    """

    PATTERNS = [
        Pattern(
            "Tax ID (Medium)",
            r"\b\d{2}\s\d{3}\s\d{3}\s\d{3}\b",
            0.3,
        ),
        Pattern(
            "Tax ID (Low)",
            r"\b\d{11}\b",
            0.01,
        ),
    ]

    CONTEXT = [
        "steuer-id",
        "steueridentifikationsnummer",
        "steuerliche identifikationsnummer",
        "steuer-idnr",
        "steuerid",
        "idnr",
        "tax id",
        "tin",
        "finanzamt",
        "identifikationsnummer",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_TAX_ID",
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

    def validate_result(self, pattern_text: str) -> bool:
        """
        Validate the pattern logic by checking the occurrence rule
        and ISO 7064 MOD 11,10 check digit.

        :param pattern_text: the text to validate.
        Only the part in text that was detected by the regex engine
        :return: A bool indicating whether the validation was successful.
        """
        text = EntityRecognizer.sanitize_value(pattern_text, self.replacement_pairs)
        digits = [int(d) for d in text]

        if len(digits) != 11:
            return False

        # First digit must not be 0
        if digits[0] == 0:
            return False

        # Occurrence rule: in the first 10 digits, exactly one digit
        # appears two or three times, all others appear zero or one time.
        first_ten = digits[:10]
        counts = [0] * 10
        for d in first_ten:
            counts[d] += 1

        twos_or_threes = sum(1 for c in counts if c >= 2)
        if twos_or_threes != 1:
            return False

        # No digit may appear more than 3 times
        if any(c > 3 for c in counts):
            return False

        # ISO 7064 MOD 11,10 check digit
        product = 10
        for i in range(10):
            total = (digits[i] + product) % 10
            if total == 0:
                total = 10
            product = (total * 2) % 11

        check = 11 - product
        if check == 10:
            check = 0

        return check == digits[10]
