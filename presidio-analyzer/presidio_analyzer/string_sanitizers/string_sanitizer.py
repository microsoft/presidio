import regex as re


class StringSanitizer:
    """Cleans a string."""

    def sanitize(self, text: str) -> str:
        return text


class RegexReplaceSanitizer(StringSanitizer):
    """
    Replace parts of a string using a regex to search the term to replace.
    """

    def __init__(self, regex: str, replace: str) -> None:
        self.regex = regex
        self.replace = replace

    def sanitize(self, text: str) -> str:
        return re.sub(self.regex, self.replace, text)


class TranslateSanitizer(StringSanitizer):
    """
    Replace characters of a string using a translate table.
    """

    def __init__(self, *trans_table) -> None:
        """
        Build sanitized using str.maketrans(...) params.

        See https://docs.python.org/3/library/stdtypes.html#str.maketrans
        """
        self.trans_table = str.maketrans(*trans_table)

    def sanitize(self, text: str) -> str:
        return text.translate(self.trans_table)


class WhiteSpaceSanitizer(TranslateSanitizer):
    """Removes all white spaces from the string"""

    def __init__(self) -> None:
        super().__init__({" ": ""})


class HyphenSanitizer(TranslateSanitizer):
    """Removes all '-' characters from the string"""

    def __init__(self) -> None:
        super().__init__({"-": ""})


class HyphenWhiteSpaceSanitizer(TranslateSanitizer):
    """Removes all '-' or white space characters from the string"""

    def __init__(self) -> None:
        super().__init__({"-": "", " ": ""})
