"""
Format Preserving encryption for PII text entities.

Uses FF1 algorithm for the encryption.
"""
from anonymizers.anonymizer import Anonymizer


# TODO implement + test
class FPE(Anonymizer):
    """
    FPE - Format Preserving Encryption.

    PII text will be replaced with a format preserving encryption using FF1 algorithm.
    """

    def __init__(self,
                 old_text: str,
                 key: str,
                 tweak: str,
                 decrypt: bool):
        self.old_text = old_text
        self.decrypt = decrypt
        self.tweak = tweak
        self.key = key

    def anonymize(self):
        """Return anonymized text using FF1 algorithm."""
        pass
