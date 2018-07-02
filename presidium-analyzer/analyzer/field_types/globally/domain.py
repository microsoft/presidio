# http://data.iana.org/TLD/tlds-alpha-by-domain.txt

import re
from field_types import field_type


class Domain(field_type.FieldType):
    name = "DOMAIN"
    context = ["domain", "website"]
    regexes = {
        "domain":
        r"((?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"
    }
