"""Mask some or all given text entity PII with given character."""
from presidio_anonymizer.anonymizers.anonymizer import Anonymizer


# TODO implement + test
class Mask(Anonymizer):
    """Mask the given text with given value."""

    def anonymize(self, params={}):
        """
        Anonymize a given amount of text with a given character.

        :return: The given text masked as requested
        """
        chars_to_replace = params.get("chars_to_replace")
        from_end = params.get("from_end")
        replace_with = params.get("replace_with")
        old_text = params.get("old_text")
        pass
