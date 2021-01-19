"""Hashes the PII text entity."""


class Hash(object):
    # TODO implement + test
    """Hash given text with sha256 algorithm."""

    def __init__(self,
                 old_text: str):
        self.old_text = old_text

    def anonymize(self):
        """
        Hash given value using sha256.

        :return: hashed original text
        """
        pass
