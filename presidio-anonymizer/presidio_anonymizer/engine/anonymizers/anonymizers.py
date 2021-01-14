import hashlib


class Anonymizers:
    def __init__(self, old_text: str):
        self.old_text = old_text

    def hash(self):
        return hashlib.sha256(self.old_text.hash_str.encode()).hexdigest()

    def fpe(self, key: str, tweak: str, decrypt: bool):
        # TODO implement
        pass

    def mask(self, replace_with: str, chars_to_replace: int,
             from_end: bool):
        # TODO implement
        pass

    def replace(self):
        pass

    def redact(self):
        pass
