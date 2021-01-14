import hashlib

# TODO implement + test
from anonymizers.anonymizer import AnonymizerAbstract


class Hash(AnonymizerAbstract):
    def __init__(self, text: str):
        self.text = text

    def annonymize(self):
        return hashlib.sha256(self.old_text.hash_str.encode()).hexdigest()
