"""Hashes the PII text entity."""
from presidio_anonymizer.anonymizers import Anonymizer


class Hash(Anonymizer):
    # TODO implement + test
    """Hash given text with sha256 algorithm."""

    def anonymize(self, text: str = None, params: dict = None) -> str:
        """
        Hash given value using sha256.

        :return: hashed original text
        """
        return params.get("old_text")

    def validate(self, params: dict = None) -> None:
        """TODO: docstring."""
        pass
