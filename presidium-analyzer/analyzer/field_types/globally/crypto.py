from hashlib import sha256
from field_types import field_type


class Crypto(field_type.FieldType):
    name = "CRYPTO"
    context = ["btc", "bitcoin", "crypto"]
    should_check_checksum = True

    regexes = {
        "btc":
        u'(?<![a-km-zA-HJ-NP-Z0-9])[13][a-km-zA-HJ-NP-Z0-9]{26,33}(?![a-km-zA-HJ-NP-Z0-9])'
    }

    digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    """Copied from:
    http://rosettacode.org/wiki/Bitcoin/address_validation#Python
    """

    def __decode_base58(bc, length):
        n = 0
        for char in bc:
            n = n * 58 + digits58.index(char)
        return n.to_bytes(length, 'big')

    def check_checksum(self):
        try:
            bcbytes = __decode_base58(self.value, 25)
            return bcbytes[-4:] == sha256(sha256(
                bcbytes[:-4]).digest()).digest()[:4]
        except Exception:
            return False
