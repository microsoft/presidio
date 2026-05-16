from typing import List, Optional, Tuple, Union

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class TrLicensePlateRecognizer(PatternRecognizer):
    """
    Recognize Turkish vehicle license plates (plaka).

    Standard civilian format: [province_code 01-81] [1-3 letters] [2-4 digits].
    Province codes: 01-81 (81 Turkish provinces).
    Letters: A-Z excluding Q, W, X (not in Turkish alphabet).

    Examples: 34 ABC 1234 (Istanbul), 06 A 123 (Ankara), 35 JK 12 (Izmir).

    Legal basis: Karayolları Trafik Kanunu (KTK) Madde 23.
    Data protection: KVKK (Kişisel Verilerin Korunması Kanunu) — license plates
    constitute personal data when linked to an identifiable vehicle owner.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
        for different strings to be used during pattern matching.
    """

    COUNTRY_CODE = "tr"

    PATTERNS = [
        Pattern(
            "TR License Plate (space)",
            r"\b(0[1-9]|[1-7][0-9]|8[0-1])\s?[A-PR-VY-Z]{1,3}\s?\d{2,4}\b",
            0.3,
        ),
        Pattern(
            "TR License Plate (hyphen)",
            r"\b(0[1-9]|[1-7][0-9]|8[0-1])-[A-PR-VY-Z]{1,3}-\d{2,4}\b",
            0.3,
        ),
    ]

    CONTEXT = [
        "plaka",
        "araç plakası",
        "plaka numarası",
        "kayıt plakası",
        "tr plaka",
        "license plate",
        "number plate",
        "plate",
        "taşıt plakası",
        "kayıt",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "tr",
        supported_entity: str = "TR_LICENSE_PLATE",
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

    def validate_result(self, pattern_text: str) -> Union[bool, None]:
        """
        Validate the matched pattern by checking province code is 01-81.

        :param pattern_text: The matched text to validated.
        Only the part in text that was detected by the regex engine
        :return: True if province code valid, False if invalid, None if not a plate
        """
        sanitized_value = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        )

        if len(sanitized_value) >= 3:
            province_code = sanitized_value[:2]
            if province_code.isdigit():
                code = int(province_code)
                return 1 <= code <= 81

        return None
