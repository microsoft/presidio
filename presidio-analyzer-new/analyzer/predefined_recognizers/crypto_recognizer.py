from analyzer import Pattern
from analyzer import PatternRecognizer
from hashlib import sha256

"""Copied from:
  http://rosettacode.org/wiki/Bitcoin/address_validation#Python
  """
CRYPTO_REGEX = r'\b[13][a-km-zA-HJ-NP-Z0-9]{26,33}\b'
CRYPTO_CONTEXT = ["wallet", "btc", "bitcoin", "crypto"]


class CryptoRecognizer(PatternRecognizer):
    """
    Recognizes common crypto account numbers using regex + checksum
    """

    def __init__(self):
        patterns = [Pattern('Crypto (Medium)', 0.5, CRYPTO_REGEX)]
        context = CRYPTO_CONTEXT
        super().__init__(supported_entities=["CRYPTO"], patterns=patterns, context=context)

    def validate_pattern_logic(self, text, pattern_result):
        # try:
        bcbytes = CryptoRecognizer.__decode_base58(text, 25)
        if bcbytes[-4:] == sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]:
            pattern_result.score = 1.0
        return pattern_result

    @staticmethod
    def __decode_base58(bc, length):
        digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        n = 0
        for char in bc:
            n = n * 58 + digits58.index(char)
        return n.to_bytes(length, 'big')
