"""
Format Preserving encryption for PII text entities.

Uses FF1 algorithm for the encryption.
"""
from presidio_anonymizer.anonymizers import Anonymizer


# TODO implement + test
class FPE(Anonymizer):
    """
    FPE - Format Preserving Encryption.

    PII text will be replaced with a format preserving encryption using FF1 algorithm.
    """

    def anonymize(self, text: str = None, params: dict = None) -> str:
        """Return anonymized text using FF1 algorithm."""
        old_text = params.get("old_text")
        decrypt = params.get("decrypt")
        tweak = params.get("tweak")
        key = params.get("key")
        return old_text + decrypt + tweak + key

    def validate(self, params: dict = None) -> None:
        """TODO: [ADO-2547] docstring."""
        pass

    def anonymizer_name(self) -> str:
        """Return anonymizer name."""
        return "fpe"
