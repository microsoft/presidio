import hashlib


# TODO implement + test
class Hash(object):
    """
    Hash given text with sha256 algorithm
    """

    def __init__(self,
                 old_text: str):
        self.old_text = old_text

    def anonymize(self):
        encoded_text = self.old_text.encode()
        return hashlib.sha256(encoded_text).hexdigest()
