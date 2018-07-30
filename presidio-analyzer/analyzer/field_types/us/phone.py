from field_types import field_type, field_pattern

class Phone(field_type.FieldType):
    name = "PHONE_NUMBER"
    context = ["phone", "number", "telephone", "cell", "mobile", "call"]
    
    # master regex: r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'

    patterns = []

    # Strong pattern: e.g., (425) 882 8080, 425 882-8080, 425.882.8080
    pattern = field_pattern.FieldPattern()
    pattern.regex = r'(\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|d{3}[-\.\s]\d{3}[-\.\s]\d{4})'
    pattern.name = 'Phone (strong)'
    pattern.strength = 0.7
    patterns.append(pattern)

    # Medium pattern: e.g., 425 8828080
    pattern = field_pattern.FieldPattern()
    pattern.regex = r'(\d{3}[-\.\s]\d{3}[-\.\s]??\d{4})'
    pattern.name = 'Phone (medium)'
    pattern.strength = 0.5
    patterns.append(pattern)

    # Weak pattern: e.g., 4258828080
    pattern = field_pattern.FieldPattern()
    pattern.regex = r'(\b\d{10}\b)'
    pattern.name = 'Phone (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)
       
    patterns.sort(key=lambda p: p.strength, reverse=True)

         

