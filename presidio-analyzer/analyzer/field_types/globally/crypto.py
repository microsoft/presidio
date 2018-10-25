from hashlib import sha256
from field_types import field_type, field_regex_pattern


class Crypto(field_type.FieldType):
    name = "CRYPTO"
    context = ["wallet", "btc", "bitcoin", "crypto"]

    should_check_checksum = True

    patterns = []

    pattern = field_regex_pattern.RegexFieldPattern()
    pattern.regex = r'\b[13][a-km-zA-HJ-NP-Z0-9]{26,33}\b'
    pattern.name = 'Crypto (Medium)'
    pattern.strength = 0.5
    patterns.append(pattern)
    """Copied from:
    http://rosettacode.org/wiki/Bitcoin/address_validation#Python
    """

    def __decode_base58(self, bc, length):
        digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        n = 0
        for char in bc:
            n = n * 58 + digits58.index(char)
        return n.to_bytes(length, 'big')

    def check_checksum(self):
        # try:
        bcbytes = self.__decode_base58(self.text, 25)
        return bcbytes[-4:] == sha256(sha256(
            bcbytes[:-4]).digest()).digest()[:4]
        # except Exception:
        #    return False
