from field_types import field_type


class UsItin(field_type.FieldType):
    name = "US_ITIN"
    context = [
        "individual",
        "taxpayer",
        "itin",
        "itins",
        "ssn",
        "tax"
        "id",
        "identification",
        "payer",
        "taxid",
        "taxpayer",
        "tin"]
    regexes = {
        "itin":
        r'(9\d{2})[- ]{0,1}((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))[- ]{0,1}(\d{4})',
    }
