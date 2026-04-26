from typing import List, Optional, Tuple, Union

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class TrPhoneNumberRecognizer(PatternRecognizer):
    """
    Recognize Turkish phone numbers (mobile and geographic).

    Turkish phone numbers follow ITU-T E.164 standard with country code +90.
    Supports both mobile numbers (starting with 5) and geographic numbers
    (starting with 2, 3, 4) for comprehensive coverage.

    Mobile Numbers:
        - 10-digit numbers starting with 5 (after country code/national prefix)
        - Mobile Number Portability (MNP) compliant - no operator validation
        - All major Turkish mobile operators: Turkcell, Vodafone, Türk Telekom

    Geographic Numbers:
        - 10-digit numbers starting with 2, 3, or 4
        - Covers major cities: Istanbul (212/216), İzmir (232), Ankara (312), etc.

    Supported formats:
        - International: +90 XXX XXX XX XX
        - National:       0 XXX XXX XX XX
        - Local:          XXX XXX XX XX

    Validation includes:
        - ITU-T E.164 compliance for Turkey (+90)
        - Format validation with boundary checks
        - Mobile/geographic number range validation
        - MNP-aware validation (no operator-specific checks)

    Reference: ITU-T E.164, Turkey country code +90.
    Legal basis: KarayollarÄ± Trafik Kanunu (KTK) Madde 23.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
        for different strings to be used during pattern matching.
    """

    PATTERNS = [
        Pattern(
            "TR Phone Number (international)",
            r"(?<!\w)\+90[\s\-]?\(?5\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}(?!\w)",
            0.4,
        ),
        Pattern(
            "TR Phone Number (national)",
            r"(?<!\w)0[\s\-]?\(?5\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}(?!\w)",
            0.3,
        ),
        Pattern(
            "TR Phone Number (local/mobile)",
            r"(?<!\w)\(?5\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}(?!\w)",
            0.15,
        ),
        # Additional patterns for geographic numbers (lower priority)
        Pattern(
            "TR Geographic Number (international)",
            r"(?<!\w)\+90[\s\-]?\(?[234]\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}(?!\w)",
            0.1,
        ),
        Pattern(
            "TR Geographic Number (national)",
            r"(?<!\w)0[\s\-]?\(?[234]\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}(?!\w)",
            0.1,
        ),
        Pattern(
            "TR Geographic Number (local)",
            r"(?<!\w)\(?[234]\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}(?!\w)",
            0.05,
        ),
    ]

    CONTEXT = [
        # Turkish terms
        "telefon",
        "telefon numarası",
        "cep telefonu",
        "cep no",
        "telefon no",
        "numara",
        "mobil telefon",
        "mobil no",
        "hücresel telefon",
        "ara",
        "ulaş",
        "iletişim",
        "bağlantı",
        "irtibat",
        "numaram",
        "telefonum",
        "cep telefonum",
        "mobil telefonum",
        "telefon numarası",
        "cep numarası",
        "mobil numarası",

        # English terms (for mixed content)
        "phone",
        "mobile",
        "cell",
        "cellphone",
        "call",
        "contact",
        "number",
        "phone number",

        # Additional context for better detection
        "sms",
        "mesaj",
        "whatsapp",
        "telegram",
        "signal",
        "viber",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "tr",
        supported_entity: str = "TR_PHONE_NUMBER",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        name: Optional[str] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs
            if replacement_pairs
            else [("-", ""), (" ", ""), ("(", ""), (")", "")]
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

    def validate_result(self, pattern_text: str) -> Union[bool, None]:
        """
        Validate the matched pattern by checking Turkish phone number format.

        Performs comprehensive validation including:
        - ITU-T E.164 compliance for Turkey (+90)
        - Mobile number format validation (starts with 5)
        - Geographic number validation (starts with 2, 3, 4)
        - Length validation for different formats
        - Mobile Number Portability (MNP) awareness

        :param pattern_text: The matched text to validate.
        Only the part in text that was detected by the regex engine.
        :return: True if valid TR phone format, False if invalid,
            None if the input cannot be parsed.
        """
        sanitized_value = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        )

        # Extract digits only
        digits = "".join(c for c in sanitized_value if c.isdigit())

        if not digits:
            return None

        # Validate based on detected format
        try:
            # International format: +90 XXXXXXXXXX (12 digits)
            if digits.startswith("90") and len(digits) == 12:
                national_number = digits[2:]  # Remove country code
                return self._validate_turkish_number(national_number)

            # National format: 0 XXXXXXXXXX (11 digits)
            elif digits.startswith("0") and len(digits) == 11:
                national_number = digits[1:]  # Remove national prefix
                return self._validate_turkish_number(national_number)

            # Local format: XXXXXXXXXX (10 digits)
            elif len(digits) == 10:
                return self._validate_turkish_number(digits)

            # Invalid length
            else:
                return False

        except (ValueError, IndexError):
            return None

    def _validate_turkish_number(self, national_number: str) -> bool:
        """
        Validate Turkish national phone number format.

        :param national_number: 10-digit national number without country/prefix
        :return: True if valid Turkish phone number
        """
        if len(national_number) != 10:
            return False

        # Check first digit for valid Turkish phone number ranges
        first_digit = national_number[0]

        # Mobile numbers: start with 5 (MNP compliant - no operator validation)
        if first_digit == "5":
            # Valid mobile area codes: 50-59 (but some ranges reserved)
            # MNP makes operator validation unreliable, so we accept all 5XX
            return True

        # Geographic numbers: start with 2, 3, 4
        elif first_digit in ("2", "3", "4"):
            # Geographic area codes have specific ranges:
            # 212, 216 (Istanbul), 224, 226, 228 (Eastern Marmara)
            # 232, 236 (Aegean), 242, 246, 248 (Mediterranean)
            # 252, 256, 258 (Central Anatolia), etc.
            # For simplicity, we accept all 2XX, 3XX, 4XX as valid geographic
            # More precise validation would require a complete area code database
            return True

        # Invalid first digit
        else:
            return False
