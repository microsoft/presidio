from field_types import field_type


class UsPassport(field_type.FieldType):
    name = "US_PASSPORT"
    context = [
        "us",
        "united",
        "states"
        "usa"
        "passport",
        "number",
        "no",
        "passport#",
        "#",
        "passportid",
        "passportno",
        "passportnumber",
        "travel",
        "document"]
    regexes = {
        "passport":
        r'[0-9]{9}\b',
    }
