from typing import List, Tuple

from presidio_analyzer import Pattern, PatternRecognizer


class EsNifRecognizer(PatternRecognizer):
    """
    Recognizes NIF number using regex and checksum
    """

    PATTERNS = [
        Pattern("NIF", r"\b[0-9]?[0-9]{7}[-]?[A-Z]\b", 0.5,),
    ]

    CONTEXT = ["documento nacional de identidad", "DNI", "NIF", "identificación"]

    def __init__(
        self,
        patterns: List[str] = None,
        context: List[str] = None,
        supported_language: str = "es",
        supported_entity: str = "ES_NIF",
        replacement_pairs: List[Tuple[str, str]] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs if replacement_pairs else [("-", ""), (" ", "")]
        )
        context = context if context else self.CONTEXT
        patterns = patterns if patterns else self.PATTERNS
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text: str):
        pattern_text = EsNifRecognizer.__sanitize_value(pattern_text)
        letter = pattern_text[-1]
        number = int("".join(filter(str.isdigit, pattern_text)))
        letters = "TRWAGMYFPDXBNJZSQVHLCKE"
        return letter == letters[number % 23]

    @staticmethod
    def __sanitize_value(text: str):
        return text.replace("-", "").replace(" ", "")
