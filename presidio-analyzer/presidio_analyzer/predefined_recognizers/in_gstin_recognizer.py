from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class InGstinRecognizer(PatternRecognizer):
    """
    Recognizes Indian GSTIN (Goods and Services Tax Identification Number).

    GSTIN is a 15-digit alphanumeric unique identifier assigned to every taxpayer
    registered under the GST system in India.
    Format:
        - First 2 digits: State code
        - Next 10 characters: PAN number of the business
        - 13th character: Entity code (alpha-numeric)
        - 14th character: Z by default
        - 15th character: Checksum (alpha-numeric)
    Reference: https://en.wikipedia.org/wiki/Goods_and_Services_Tax_(India)

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "GSTIN (High)",
            r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}Z[A-Z0-9]{1}\b",
            0.5,
        ),
    ]

    CONTEXT = [
        "gstin",
        "goods and services tax",
        "gst number",
        "gst identification",
        "taxpayer id",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "IN_GSTIN",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            patterns=patterns,
            context=context,
            supported_language=supported_language,
            supported_entity=supported_entity,
        )


    def validate_result(self, pattern_text: str) -> Optional[float]:
        if len(pattern_text) != 15:
            return 0.0
        base = pattern_text[:14]
        checksum_char = pattern_text[14]
        calculated_checksum = self._calculate_checksum(base)
        return 1.0 if checksum_char.upper() == calculated_checksum else 0.0
    
    def _calculate_checksum(self, gstin_without_checksum: str) -> str:
        charset = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        factor = 2
        total = 0
        for char in reversed(gstin_without_checksum):
            code_point = charset.index(char)
            addend = factor * code_point
            total += (addend // 36) + (addend % 36)
            factor = 1 if factor == 2 else 2
        remainder = total % 36
        check_code_point = (36 - remainder) % 36
        return charset[check_code_point]
