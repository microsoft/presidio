# TODO implement + test
from anonymizers.anonymizer import AnonymizerAbstract


class FPE(AnonymizerAbstract):
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
