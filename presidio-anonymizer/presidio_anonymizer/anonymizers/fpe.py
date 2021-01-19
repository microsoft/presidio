"""
Format Preserving encryption for PII text entities.

Uses FF1 algorithm for the encryption.
"""
from presidio_anonymizer.anonymizers.anonymizer import Anonymizer


# TODO implement + test
class FPE(Anonymizer):
    """
    FPE - Format Preserving Encryption.

    PII text will be replaced with a format preserving encryption using FF1 algorithm.
    """

    def anonymize(self, params={}):
        old_text = params.get("old_text")
        decrypt = params.get("decrypt")
        tweak = params.get("tweak")
        key = params.get("key")
        """Return anonymized text using FF1 algorithm."""
        pass
