from field_types import field_type, field_pattern


class UsItin(field_type.FieldType):
    name = "US_ITIN"
    context = [
        "individual",
        "taxpayer",
        "itin",
        "tax",
        "payer",
        "taxid",
        "tin"]
    
    # Master Regex: r'\b(9\d{2})[- ]{0,1}((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))[- ]{0,1}(\d{4})\b',

    patterns = []

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'(\b(9\d{2})[- ]{1}((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))(\d{4})\b)|(\b(9\d{2})((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))[- ]{1}(\d{4})\b)'
    pattern.name = 'Itin (very weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b(9\d{2})((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))(\d{4})\b'                 
    pattern.name = 'Itin (weak)'
    pattern.strength = 0.3
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b(9\d{2})[- ]{1}((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))[- ]{1}(\d{4})\b'
    pattern.name = 'Itin (medium)'
    pattern.strength = 0.5
    patterns.append(pattern)

    patterns.sort(key=lambda p: p.strength, reverse=True)
