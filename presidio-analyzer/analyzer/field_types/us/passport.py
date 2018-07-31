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

    # Weak pattern: all passport numbers are a weak match, e.g., 14019033
    pattern = field_pattern.FieldPattern()
    pattern.regex = r'(\b[0-9]{9}\b)'
    pattern.name = 'Passport (very weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

