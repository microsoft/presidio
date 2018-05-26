import re

from field_types import field_type


class Crypto(field_type.FieldType):
    name = "CRYPTO"
    context = []
    regexes = {
        "btc": re.compile(
            u'(?<![a-km-zA-HJ-NP-Z0-9])[13][a-km-zA-HJ-NP-Z0-9]{26,33}(?![a-km-zA-HJ-NP-Z0-9])')
    }
