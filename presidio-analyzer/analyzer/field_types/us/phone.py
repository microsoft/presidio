from field_types import field_type, field_pattern

class Phone(field_type.FieldType):
    name = "PHONE_NUMBER"
    context = ["phone", "number", "telephone", "cell", "mobile", "call"]
    
    # master regex: r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'

    patterns = []
    pattern = field_pattern.FieldPattern()
    pattern.name = 'Strong'
    pattern.regex = r'(\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|d{3}[-\.\s]\d{3}[-\.\s]\d{4})'
    pattern.strength = 0.7
    pattern.examples = {'(425) 882 8080', '425 882-8080', '425.882.8080'}
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.name = 'Medium'
    pattern.regex = r'(\d{3}[-\.\s]\d{3}[-\.\s]??\d{4})'
    pattern.strength = 0.5
    pattern.examples = {'425 8828080'}
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.name = 'Low'
    pattern.regex = r'(\b\d{10}\b)'
    pattern.strength = 0.2
    pattern.examples = {'4258828080'}
    patterns.append(pattern)
       
    patterns.sort(key=lambda p: p.strength, reverse=True)

         

