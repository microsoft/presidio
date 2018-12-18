from field_types import field_type
import re2 as re


class Ner(field_type.FieldType):
    name = "ner"
    context = []

    def validate_result(self):
        pattern = r"^[a-zA-Z0-9-_'.() ]+$"
        guid_pattern = r"(\{){0,1}[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}(\}){0,1}"  # noqa: E501
        result = re.match(pattern, self.text, re.IGNORECASE | re.UNICODE)
        if result is not None:
            if len(self.text) > 16:
                if re.match(guid_pattern, self.text,
                            re.IGNORECASE | re.UNICODE) is not None:
                    return False
            return True

        return False

    def check_label(self, label):
        if self.name == "LOCATION" and (label == 'GPE' or label == 'LOC'):
            return True

        if self.name == "PERSON" and label == 'PERSON':
            return True

        if self.name == "DATE_TIME" and (label == 'DATE' or label == 'TIME'):
            return True

        if self.name == "NRP" and label == 'NORP':
            return True

        return False
