from hashlib import sha256
from typing import List

from presidio_analyzer import Pattern, PatternRecognizer

# Copied from:
# http://rosettacode.org/wiki/Bitcoin/address_validation#Python


class CryptoRecognizer(PatternRecognizer):
    """
    Recognizes common crypto account numbers using regex + checksum
    """

    PATTERNS = [
        Pattern("Crypto (Medium)", r"\b[13][a-km-zA-HJ-NP-Z1-9]{26,33}\b", 0.5),
    ]

    CONTEXT = ["wallet", "btc", "bitcoin", "crypto"]

    def __init__(
        self,
        patterns: List[str] = None,
        context: List[str] = None,
        supported_language: str = "en",
        supported_entity: str = "CRYPTO",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text:str):
        try:
            bcbytes = self.__decode_base58(pattern_text, 25)
            return bcbytes[-4:] == sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]
        except ValueError:
            return False

    @staticmethod
    def __decode_base58(bc, length: int):
        digits58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        n = 0
        for char in bc:
            n = n * 58 + digits58.index(char)
        return n.to_bytes(length, "big")
