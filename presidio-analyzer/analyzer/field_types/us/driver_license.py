from field_types import field_type


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
    regexes = {
        'AL': r'^[0-9]{1,7}\b',
        'AK': r'^[0-9]{1,7}\b',
        'AZ': r'^[a-z][0-9]{8}\b|[0-9]{9}\b',
        'AR': r'^[0-9]{4,9}\b',
        'CA': r'^[a-z]{1}[0-9]{7}\b',
        'CO': r'^[0-9]{9}\b|[a-z]{1}[0-9]{3,6}\b|[a-z]{2}[0-9]{2,5}\b',
        'CT': r'^[0-9]{9}\b',
        'DE': r'^[0-9]{1,7}\b',
        'DC': r'^[0-9]{7}\b|[0-9]{9}\b',
        'FL': r'^[a-z]{1}[0-9]{1,12}\b',
        'GA': r'^[0-9]{7,9}\b',
        'HI': r'^[0-9]{9}\b|H[0-9]{8}\b',
        'ID': r'^[0-9]{9}\b|[a-z]{2}[0-9]{6}[a-z]{1}\b',
        'IL': r'^[a-z]{1}[0-9]{11,12}',
        'IN': r'^[a-z]{1}[0-9]{9}\b|[0-9]{9,10}\b',
        'IA': r'^[0-9]{9}\b|[0-9]{3}[a-z]{2}[0-9]{4}\b',
        'KS': r'^[a-z]{1}[0-9]{1}[a-z]{1}[0-9]{1}[a-z]{1}\b|[a-z]{1}[0-9]{8}\b|[0-9]{9}\b',
        'KY': r'^[a-z]{1}[0-9]{8}\b|[0-9]{9}\b',
        'LA': r'^[0-9]{9}\b',
        'ME': r'^[0-9]{7}\b|[0-9]{8}\b|[0-9]{8}[a-z]{1}\b',
        'MD': r'^[a-z]{1}[0-9]{12}\b',
        'MA': r'^[a-z][0-9]{8}\b|[0-9]{9}\b',
        'MI': r'^[a-z]{1}[0-9]{12}\b|[a-z]{1}[0-9]{10}\b',
        'MN': r'^[a-z]{1}[0-9]{12}\b',
        'MS': r'^[0-9]{9}\b',
        'MO': r'^[a-z]{1}[0-9]{5,9}\b|[a-z]{1}[0-9]{6}R\b|[0-9]{9}\b|[0-9]{8}[a-z]{2}\b|[0-9]{9}[a-z]{1}\b',
        'MT': r'^[0-9]{13,14}\b|[a-z]{9}\b|[a-z]{1}[0-9]{8}\b',
        'NE': r'^[a-z]{1}[0-9]{6,8}\b',
        'NV': r'^[0-9]{9,10}\b|[0-9]{12}\b|x[0-9]{8}\b',
        'NH': r'^[0-9]{2}[a-z]{3}[0-9]{5}b',
        'NJ': r'^[a-z]{1}[0-9]{14}\b',
        'NM': r'^[0-9]{8,9}\b',
        'NY': r'^[a-z]{1}[0-9]{7}\b|[a-z]{1}[0-9]{18}\b|[0-9]{8,9}\b|[0-9]{16}\b|[a-z]{8}\b',
        'NC': r'^[0-9]{1,12}\b',
        'ND': r'^[a-z]{3}[0-9]{6}\b|[0-9]{9}\b',
        'OH': r'^[a-z]{1}[0-9]{4,8}\b|[a-z]{2}[0-9]{3,7}\b|[0-9]{8}\b',
        'OK': r'^[a-z]{1}[0-9]{9}\b|[0-9]{9}\b',
        'OR': r'^[0-9]{1,9}\b',
        'PA': r'^[0-9]{8}\b',
        'RI': r'^[0-9]{7}\b|v[0-9]{6}\b',
        'SC': r'^[0-9]{5,11}\b',
        'SD': r'^[0-9]{6,10}\b|[0-9]{12}',
        'TN': r'^[0-9]{7,9}\b',
        'TX': r'^[0-9]{7-8}\b',
        'UT': r'^[0-9]{4,10}\b',
        'VT': r'^[0-9]{8}\b|[0-9]{7}[a-z]\b',
        'VA': r'^[a-z][0-9]{9,11}\b|[0-9]{9}\b',
        'WA': r'^[a-z*]{7}[0-9]{3}[0-9a-z]{2}\b',
        'WV': r'^[0-9]{7}\b|[a-z]{1,2}[0-9]{5,6}\b',
        'WI': r'^[a-z]{1}[0-9]{13}\b',
        'WY': r'^[0-9]{9-10}\b'
    }

    def __init__(self):

        # Remove duplicates regex. We keep the original dictionary for future
        # use cases
        new_regexes = dict()
        for regex in self.regexes.values():
            splitted = regex.split('|')
            for split in splitted:
                if split not in new_regexes.values():
                    new_regexes[str(len(new_regexes) + 1)] = split
        self.regexes = new_regexes
