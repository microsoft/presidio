import re
from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer

from .za_id_number_recognizer import ZaIdNumberRecognizer


class ZaDriverLicenseRecognizer(PatternRecognizer):
    """
    Recognize South African driver's licence numbers issued by eNaTIS.

    eNaTIS licence numbers are alphanumeric strings of roughly 10–12
    characters combining digit blocks with trailing letter groups.

    Reference:
    https://github.com/ugommirikwe/sa-license-decoder/blob/master/SPEC.md

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    COUNTRY_CODE = "za"

    MIN_LENGTH = 10
    MAX_LENGTH = 14

    PATTERNS = [
        Pattern(
            "South African Driver's Licence",
            r"\b\d{6,10}[A-Z0-9]{2,5}\b",
            0.3,
        ),
    ]

    CONTEXT = [
        "licence",
        "license",
        "driving licence",
        "driving license",
        "driver's licence",
        "driver's license",
        "drivers licence",
        "drivers license",
        "enatis",
        "natis",
        "licence number",
        "license number",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "ZA_DRIVER_LICENSE",
        name: Optional[str] = None,
    ):
        patterns = self.PATTERNS if patterns is None else patterns
        context = self.CONTEXT if context is None else context
        self._id_validator = ZaIdNumberRecognizer()
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
            name=name,
        )

    def validate_result(self, pattern_text: str) -> bool:  # noqa: D102
        text = pattern_text.upper()
        if not self.MIN_LENGTH <= len(text) <= self.MAX_LENGTH:
            return False
        if not re.search(r"\d", text) or not re.search(r"[A-Z]", text):
            return False
        if text.isdigit() and self._id_validator.validate_result(text):
            return False
        return True
