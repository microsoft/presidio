from field_types import field_type, field_pattern

class UsPassport(field_type.FieldType):
    name = "US_PASSPORT"
    context = [
        "us",
        "united",
        "states",
        "passport",
        "number",
        "passport#",
        "travel",
        "document"]

    patterns = []

    pattern = field_pattern.FieldPattern()
    pattern.name = 'Passport (weak)'
    pattern.regex = r'(\b[0-9]{9}\b)'
    pattern.strength = 0.05
    pattern.examples = {'140514722'}
    patterns.append(pattern)

