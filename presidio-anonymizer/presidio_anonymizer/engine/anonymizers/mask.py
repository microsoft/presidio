# TODO implement + test
from anonymizers.anonymizer import AnonymizerAbstract


class Mask(AnonymizerAbstract):
    def __init__(self, old_text: str, replace_with: str, chars_to_replace: int,
                 from_end: bool):
        self.chars_to_replace = chars_to_replace
        self.from_end = from_end
        self.replace_with = replace_with
        self.old_text = old_text

    def anonymize(self):
        pass
