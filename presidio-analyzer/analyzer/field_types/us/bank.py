from field_types import field_type, field_regex_pattern


class UsBank(field_type.FieldType):
    name = "US_BANK_NUMBER"
    context = [
        "bank"
        "checking",  #TODO: change to "checking account" as part of keyphrase change
        "account",
        "account#",
        "acct",
        "saving",
        "debit"
    ]

    patterns = []

    # Weak pattern: all passport numbers are a weak match, e.g., 14019033
    pattern = field_regex_pattern.RegexFieldPattern()
    pattern.regex = r'\b[0-9]{8,17}\b'
    pattern.name = 'Bank Account (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)
