from presidio_analyzer import Pattern, PatternRecognizer


class CreditCardRecognizer(PatternRecognizer):
    """
    Recognizes common credit card numbers using regex + checksum
    """

    # pylint: disable=line-too-long
    PATTERNS = [
        Pattern(
            "All Credit Cards (weak)",
            r"\b((4\d{3})|(5[0-5]\d{2})|(6\d{3})|(1\d{3})|(3\d{3}))[- ]?(\d{3,4})[- ]?(\d{3,4})[- ]?(\d{3,5})\b",  # noqa: E501
            0.3,
        ),
    ]

    CONTEXT = [
        "credit",
        "card",
        "visa",
        "mastercard",
        "cc ",
        # "american express" #Task #603: Support keyphrases
        "amex",
        "discover",
        "jcb",
        "diners",
        "maestro",
        "instapayment",
    ]

    def __init__(
        self,
        patterns=None,
        context=None,
        supported_language="en",
        supported_entity="CREDIT_CARD",
        replacement_pairs=None,
    ):
        """
            :param replacement_pairs: list of tuples to replace in the string.
                ( default: [("-", ""), (" ", "")] )
                i.e. remove dashes and spaces from the string during recognition.
        """
        self.replacement_pairs = replacement_pairs \
            if replacement_pairs \
            else [("-", ""), (" ", "")]
        context = context if context else self.CONTEXT
        patterns = patterns if patterns else self.PATTERNS
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text):
        sanitized_value = self.__sanitize_value(pattern_text, self.replacement_pairs)
        checksum = self.__luhn_checksum(sanitized_value)

        return checksum

    @staticmethod
    def __luhn_checksum(sanitized_value):
        def digits_of(n):
            return [int(d) for d in str(n)]

        digits = digits_of(sanitized_value)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10 == 0

    @staticmethod
    def __sanitize_value(text, replacement_pairs):
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text
