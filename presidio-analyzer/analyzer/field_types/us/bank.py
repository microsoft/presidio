from field_types import field_type


class UsBank(field_type.FieldType):
    name = "US_BANK_NUMBER"
    context = [
        "us",
        "united",
        "states"
        "checking",
        "number",
        "account",
        "account#",
        "#",
        "acct",
        "saving",
        "debit"
        "bank"]
    regexes = {
        "bank": r'[0-9]{8,17}\b',
    }
