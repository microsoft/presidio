"""Mask some or all given text entity PII with given character."""
from anonymizers.anonymizer import Anonymizer


# TODO implement + test
class Mask(Anonymizer):
    """Mask the given text with given value."""

    def __init__(self,
                 old_text: str,
                 replace_with: str,
                 chars_to_replace: int,
                 from_end: bool):
        self.chars_to_replace = chars_to_replace
        self.from_end = from_end
        self.replace_with = replace_with
        self.old_text = old_text

    def anonymize(self):
        """
        Anonymize a given amount of text with a given character.

        :return: The given text masked as requested
        """
        pass
