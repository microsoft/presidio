from hashlib import sha256
from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer

# Copied from:
# http://rosettacode.org/wiki/Bitcoin/address_validation#Python
REGEX = r'\b[13][a-km-zA-HJ-NP-Z1-9]{26,33}\b'
CONTEXT = ["wallet", "btc", "bitcoin", "crypto"]


class CryptoRecognizer(PatternRecognizer):
    """
    Recognizes common crypto account numbers using regex + checksum
    """

    def __init__(self):
        patterns = [Pattern('Crypto (Medium)', REGEX, 0.5)]
        super().__init__(supported_entity="CRYPTO", patterns=patterns,
                         context=CONTEXT)

    def validate_result(self, pattern_text):
        try:
            bcbytes = CryptoRecognizer.__decode_base58(pattern_text, 25)
            return bcbytes[-4:] == sha256(sha256(bcbytes[:-4])
                                          .digest()).digest()[:4]
        except ValueError:
            return False

    @staticmethod
    def __decode_base58(bc, length):
        digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        n = 0
        for char in bc:
            n = n * 58 + digits58.index(char)
        return n.to_bytes(length, 'big')
