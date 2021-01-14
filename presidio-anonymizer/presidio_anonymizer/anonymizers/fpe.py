# TODO implement + test
from anonymizers.anonymizer import Anonymizer


class FPE(Anonymizer):
    """
    Current text will be transformed into FPE -
    Format Preserving Encryption using FF1 algorithm.
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
        pass
