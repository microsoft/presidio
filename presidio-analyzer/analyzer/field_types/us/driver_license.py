from field_types import field_type, field_pattern


class UsDriverLicense(field_type.FieldType):

    name = "US_DRIVER_LICENSE"
    context = [
        "driver",
        "license",
        "permit",
        "id",
        "lic",
        "identification",
        "card",
        "cards",
        "dl",
        "dls",
        "cdls",
        "id",
        "lic#"]

    # List from https://ntsi.com/drivers-license-format/
    # ---------------
    patterns = []

     # WA Driver License number is relatively unique as it also includes '*' chars
    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b([A-Z][A-Z0-9*]{11})\b'
    pattern.name = 'Driver License - WA (weak) '
    pattern.strength = 0.3
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b([A-Z][0-9]{3,6}|[A-Z][0-9]{5,9}|[A-Z][0-9]{6,8}|[A-Z][0-9]{4,8}|[A-Z][0-9]{9,11}|[A-Z]{1,2}[0-9]{5,6}|H[0-9]{8}|V[0-9]{6}|X[0-9]{8}|A-Z]{2}[0-9]{2,5}|[A-Z]{2}[0-9]{3,7}|[0-9]{2}[A-Z]{3}[0-9]{5,6}|[A-Z][0-9]{13,14}|[A-Z][0-9]{18}|[A-Z][0-9]{6}R|[A-Z][0-9]{9}|[A-Z][0-9]{1,12}|[0-9]{9}[A-Z]|[A-Z]{2}[0-9]{6}[A-Z]|[0-9]{8}[A-Z]{2}|[0-9]{3}[A-Z]{2}[0-9]{4}|[A-Z][0-9][A-Z][0-9][A-Z]|[0-9]{7,8}[A-Z])\b'
    pattern.name = 'Driver License - Alphanumeric (weak) '
    pattern.strength = 0.3
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b([0-9]{1,9}|[0-9]{4,10}|[0-9]{6,10}|[0-9]{1,12}|[0-9]{12,14}|[0-9]{16})\b'
    pattern.name = 'Driver License - Digits (very weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b([A-Z]{7,9})\b'
    pattern.name = 'Driver License - Letters (very weak)'
    pattern.strength = 0.00
    patterns.append(pattern)

    patterns.sort(key=lambda p: p.strength, reverse=True)


    # ----------
    '''  patterns = []

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{1,7}\b'
    pattern.name = 'AL, AK (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{8}\b|[0-9]{9}\b'
    pattern.name = 'AZ (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{4,9}\b'
    pattern.name = 'AR - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{7}\b'
    pattern.name = 'CA - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{7,8}|[0-9]{9,10}|\b'
    pattern.name = 'CO, LA, MS, PA, WY, TN, TX, VT, OR - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{3,6}\b|[A-Z]{2}[0-9]{2,5}\b'
    pattern.name = 'CO - (weak2)'
    pattern.strength = 0.1
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{9}\b'
    pattern.name = 'CT, IA - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{1,7}\b'
    pattern.name = 'DE - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{7}\b|[0-9]{9}\b'
    pattern.name = 'DC - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{1,12}\b'
    pattern.name = 'FL - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{7,9}\b'
    pattern.name = 'GA - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{9}\b'
    pattern.name = 'HI - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\bH[0-9]{8}\b'
    pattern.name = 'HI - (weak2)'
    pattern.strength = 0.3
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{9}\b'
    pattern.name = 'ID - (weak)'
    pattern.strength = 0.05

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z]{2}[0-9]{6}[A-Z]\b'
    pattern.name = 'ID - (Medium)'
    pattern.strength = 0.4
    patterns.append(pattern)
    
    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{11,12}'
    pattern.name = 'IL - (weak)'
    pattern.strength = 0.2
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{9,10}\b'
    pattern.name = 'IN - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{9}\b|\b'
    pattern.name = 'IN - (weak2)'
    pattern.strength = 0.2
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{9}\b'
    pattern.name = 'IA - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'[0-9]{3}[A-Z]{2}[0-9]{4}\b'
    pattern.name = 'IA - (weak2)'
    pattern.strength = 0.2
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9][A-Z][0-9][A-Z]\b'
    pattern.name = 'KS - (medium)'
    pattern.strength = 0.4
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'[A-Z][0-9]{8}\b'
    pattern.name = 'IA - (weak)'
    pattern.strength = 0.2
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9][A-Z][0-9][A-Z]\b|[A-Z][0-9]{8}\b|[0-9]{9}\b'
    pattern.name = 'IA - (weak2)'
    pattern.strength = 0.2
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{7}\b|[0-9]{8}\b|[0-9]{8}[A-Z]\b'
    pattern.name = 'ME - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{12}\b'
    pattern.name = 'MD - (weak)'
    pattern.strength = 0.2
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{8}\b'
    pattern.name = 'MA - (weak)'
    pattern.strength = 0.2
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{12}\b|[A-Z][0-9]{10}\b'
    pattern.name = 'MI, MN - (weak)'
    pattern.strength = 0.2
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{5,9}\b|[A-Z][0-9]{6}R\b|[0-9]{9}\b|[0-9]{8}[A-Z]{2}\b|[0-9]{9}[A-Z]\b'
    pattern.name = 'MO - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{13,14}\b|[A-Z]{9}\b|[A-Z][0-9]{8}\b'
    pattern.name = 'MT - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{6,8}\b'
    pattern.name = 'NE - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{9,10}\b|[0-9]{12}\b|x[0-9]{8}\b'
    pattern.name = 'NV - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{2}[A-Z]{3}[0-9]{5}b'
    pattern.name = 'NH - (weak)'
    pattern.strength = 0.2
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{14}\b'
    pattern.name = 'NJ - (weak)'
    pattern.strength = 0.2
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{14}\b'
    pattern.name = 'NJ - (weak)'
    pattern.strength = 0.2
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{8,9}\b'
    pattern.name = 'NM - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    #TODO: break into weak and medium strength
    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{7}\b|[A-Z][0-9]{18}\b|[0-9]{8,9}\b|[0-9]{16}\b|[A-Z]{8}\b'
    pattern.name = 'NY - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{1,12}\b'
    pattern.name = 'NC - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z]{3}[0-9]{6}\b|[0-9]{9}\b'
    pattern.name = 'ND - (weak)'
    pattern.strength = 0.2
    patterns.append(pattern)

    #TODO: break into weak and medium strength
    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{4,8}\b|[A-Z]{2}[0-9]{3,7}\b|[0-9]{8}\b'
    pattern.name = 'OH - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{9}\b|[0-9]{9}\b'
    pattern.name = 'OK - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{7}\b'
    pattern.name = 'RI - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\bv[0-9]{6}\b'
    pattern.name = 'RI - (weak2)'
    pattern.strength = 0.2
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{5,11}\b'
    pattern.name = 'SC - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{6,10}\b|[0-9]{12}'
    pattern.name = 'SD - (weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[0-9]{7}[A-Z]\b'
    pattern.name = 'VT - (weak)'
    pattern.strength = 0.1
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{9,11}\b'
    pattern.name = 'VA - (weak)'
    pattern.strength = 0.2
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[a-z*]{7}[0-9]{3}[0-9a-z]{2}\b'
    pattern.name = 'WA - (Medium)'
    pattern.strength = 0.5
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z]{1,2}[0-9]{5,6}\b'
    pattern.name = 'WA - (weak)'
    pattern.strength = 0.1
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z]{1,2}[0-9]{5,6}\b'
    pattern.name = 'WV - (weak)'
    pattern.strength = 0.1
    patterns.append(pattern)

    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b[A-Z][0-9]{13}\b'
    pattern.name = 'WI - (weak)'
    pattern.strength = 0.3
    patterns.append(pattern)
    
    patterns.sort(key=lambda p: p.strength, reverse=True)
    '''
    # Regex per state
    '''
    regexes = {
        'AL': r'^[0-9]{1,7}\b',
        'AK': r'^[0-9]{1,7}\b',
        'AZ': r'\b[A-Z][0-9]{8}\b|[0-9]{9}\b',
        'AR': r'^[0-9]{4,9}\b',
        'CA': r'\b[A-Z][0-9]{7}\b',
        'CO': r'^[0-9]{9}\b|[A-Z][0-9]{3,6}\b|[A-Z]{2}[0-9]{2,5}\b',
        'CT': r'^[0-9]{9}\b',
        'DE': r'^[0-9]{1,7}\b',
        'DC': r'^[0-9]{7}\b|[0-9]{9}\b',
        'FL': r'\b[A-Z][0-9]{1,12}\b',
        'GA': r'^[0-9]{7,9}\b',
        'HI': r'^[0-9]{9}\b|H[0-9]{8}\b',
        'ID': r'^[0-9]{9}\b|[A-Z]{2}[0-9]{6}[A-Z]\b',
        'IL': r'\b[A-Z][0-9]{11,12}',
        'IN': r'\b[A-Z][0-9]{9}\b|[0-9]{9,10}\b',
        'IA': r'^[0-9]{9}\b|[0-9]{3}[A-Z]{2}[0-9]{4}\b',
        'KS': r'\b[A-Z][0-9][A-Z][0-9][A-Z]\b|[A-Z][0-9]{8}\b|[0-9]{9}\b',
        'KY': r'\b[A-Z][0-9]{8}\b|[0-9]{9}\b',
        'LA': r'^[0-9]{9}\b',
        'ME': r'^[0-9]{7}\b|[0-9]{8}\b|[0-9]{8}[A-Z]\b',
        'MD': r'\b[A-Z][0-9]{12}\b',
        'MA': r'\b[A-Z][0-9]{8}\b|[0-9]{9}\b',
        'MI': r'\b[A-Z][0-9]{12}\b|[A-Z][0-9]{10}\b',
        'MN': r'\b[A-Z][0-9]{12}\b',
        'MS': r'^[0-9]{9}\b',
        'MO': r'\b[A-Z][0-9]{5,9}\b|[A-Z][0-9]{6}R\b|[0-9]{9}\b|[0-9]{8}[A-Z]{2}\b|[0-9]{9}[A-Z]\b',
        'MT': r'^[0-9]{13,14}\b|[A-Z]{9}\b|[A-Z][0-9]{8}\b',
        'NE': r'\b[A-Z][0-9]{6,8}\b',
        'NV': r'^[0-9]{9,10}\b|[0-9]{12}\b|x[0-9]{8}\b',
        'NH': r'^[0-9]{2}[A-Z]{3}[0-9]{5}b',
        'NJ': r'\b[A-Z][0-9]{14}\b',
        'NM': r'^[0-9]{8,9}\b',
        'NY': r'\b[A-Z][0-9]{7}\b|[A-Z][0-9]{18}\b|[0-9]{8,9}\b|[0-9]{16}\b|[A-Z]{8}\b',
        'NC': r'^[0-9]{1,12}\b',
        'ND': r'\b[A-Z]{3}[0-9]{6}\b|[0-9]{9}\b',
        'OH': r'\b[A-Z][0-9]{4,8}\b|[A-Z]{2}[0-9]{3,7}\b|[0-9]{8}\b',
        'OK': r'\b[A-Z][0-9]{9}\b|[0-9]{9}\b',
        'OR': r'^[0-9]{1,9}\b',
        'PA': r'^[0-9]{8}\b',
        'RI': r'^[0-9]{7}\b|v[0-9]{6}\b',
        'SC': r'^[0-9]{5,11}\b',
        'SD': r'^[0-9]{6,10}\b|[0-9]{12}',
        'TN': r'^[0-9]{7,9}\b',
        'TX': r'^[0-9]{7-8}\b',
        'UT': r'^[0-9]{4,10}\b',
        'VT': r'^[0-9]{8}\b|[0-9]{7}[A-Z]\b',
        'VA': r'\b[A-Z][0-9]{9,11}\b|[0-9]{9}\b',
        'WA': r'^[a-z*]{7}[0-9]{3}[0-9a-z]{2}\b',
        'WV': r'^[0-9]{7}\b|[A-Z]{1,2}[0-9]{5,6}\b',
        'WI': r'\b[A-Z][0-9]{13}\b',
        'WY': r'^[0-9]{9-10}\b'
    }
    '''
