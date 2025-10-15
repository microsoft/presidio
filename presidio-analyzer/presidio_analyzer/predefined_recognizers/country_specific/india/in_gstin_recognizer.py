from typing import List, Optional, Tuple

from presidio_analyzer import Pattern, PatternRecognizer


class InGstinRecognizer(PatternRecognizer):
    """
    Recognizes Indian Goods and Services Tax Identification Number ("GSTIN").

    The GSTIN is a 15-character identifier with the following structure:
    - First 2 digits: State code (01-37)
    - Next 10 digits: PAN of the entity
    - 13th digit: Registration number for same PAN in the state
    - 14th digit: 'Z'
    - 15th digit: Checksum

    Reference: https://www.gst.gov.in/
    This recognizer identifies GSTIN using regex and context words.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    for different strings to be used during pattern matching.
    This can allow a greater variety in input, for example by removing dashes or spaces.
    """

    PATTERNS = [
        Pattern(
            "GSTIN (High)",
            r"\b((?:0[1-9]|[1-3][0-7])[A-Za-z0-9]{10}[A-Za-z0-9]{1}Z[A-Za-z0-9]{1})\b",
            0.8,
        ),
        Pattern(
            "GSTIN (Medium)",
            r"\b((?:0[1-9]|[1-3][0-7])[A-Za-z0-9]{11}Z[A-Za-z0-9]{1})\b",
            0.4,
        ),
        Pattern(
            "GSTIN (Low)",
            r"\b([0-9]{2}[A-Za-z0-9]{11}Z[A-Za-z0-9]{1})\b",
            0.1,
        ),
    ]

    CONTEXT = [
        "gstin",
        "gst",
        "goods and services tax",
        "tax identification",
        "gst number",
        "gst registration",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "IN_GSTIN",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
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
        )
        self.supported_entity = supported_entity

    def validate_result(self, pattern_text: str) -> bool:
        """
        Validate the GSTIN format and structure.

        :param pattern_text: The text pattern to validate
        :return: True if the GSTIN is valid, False otherwise
        """
        sanitized_value = self._sanitize_value(pattern_text)
        return self._validate_gstin(sanitized_value)

    def _sanitize_value(self, text: str) -> str:
        """Remove common separators and normalize the text."""
        import re

        # First, try to extract GSTIN pattern from the text
        gstin_pattern = (
            r'\b((?:0[1-9]|[1-3][0-7])[A-Za-z]{5}[0-9]{4}[A-Za-z]{1}'
            r'[0-9A-Za-z]{1}Z[0-9A-Za-z]{1})\b'
        )
        match = re.search(gstin_pattern, text.upper())
        if match:
            return match.group(1)

        # If no GSTIN pattern found, sanitize the entire text
        sanitized = text.upper()
        for old, new in self.replacement_pairs:
            sanitized = sanitized.replace(old, new)
        return sanitized

    def _validate_gstin(self, gstin: str) -> bool:
        """
        Validate GSTIN structure and format.

        :param gstin: The GSTIN string to validate
        :return: True if valid, False otherwise
        """
        if len(gstin) != 15:
            return False

        # Check state code (first 2 digits should be 01-37)
        state_code = gstin[:2]
        if not state_code.isdigit() or not (1 <= int(state_code) <= 37):
            return False

        # Check PAN format (characters 3-12)
        pan_part = gstin[2:12]
        if not self._validate_pan_format(pan_part):
            return False

        # Check 13th character (registration number)
        reg_number = gstin[12]
        if not reg_number.isalnum():
            return False

        # Check 14th character should be 'Z'
        if gstin[13] != 'Z':
            return False

        # Check 15th character (checksum)
        checksum = gstin[14]
        if not checksum.isalnum():
            return False

        return True

    def _validate_pan_format(self, pan: str) -> bool:
        """
        Validate PAN format within GSTIN.

        PAN format: 5 letters + 4 digits + 1 letter
        However, some valid PANs may have digits in the first 5 characters.

        :param pan: The PAN part of GSTIN (10 characters)
        :return: True if valid PAN format, False otherwise
        """
        if len(pan) != 10:
            return False

        # Check that it contains a mix of letters and digits
        # At least 3 letters in the first 5 characters
        first_five = pan[:5]
        letter_count = sum(1 for c in first_five if c.isalpha())
        if letter_count < 3:
            return False

        # Characters 6-9 should be digits
        if not pan[5:9].isdigit():
            return False

        # 10th character should be a letter
        if not pan[9].isalpha():
            return False

        return True
