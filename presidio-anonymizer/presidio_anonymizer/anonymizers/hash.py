"""Hashes the PII text entity."""
from presidio_anonymizer.anonymizers import Anonymizer


class Hash(Anonymizer):
    # TODO implement + test
    """Hash given text with sha256 algorithm."""

    def anonymize(self, original_text=None, params={}):
        """
        Hash given value using sha256.

        :return: hashed original text
        """
        return params.get("old_text")
