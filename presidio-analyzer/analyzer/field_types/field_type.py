

class FieldType(object):

    name = "Field Type Name"
    text = ""
    patterns = []
    contexts = []
    should_check_checksum = False

    def check_checksum(self):
        return False
