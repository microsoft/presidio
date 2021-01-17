# TODO implement + test
from anonymizers.anonymizer import Anonymizer


class Replace(Anonymizer):
    """
    Replaces text with new string value
    """

    def __init__(self,
                 new_text: str):
        self.new_text = new_text

    def anonymize(self):
        pass
