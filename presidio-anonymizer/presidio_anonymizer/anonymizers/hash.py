"""Hashes the PII text entity."""


class Hash(object):
    # TODO implement + test
    """Hash given text with sha256 algorithm."""

    def anonymize(self, params={}):
        old_text = params.get("old_text")
        """
        Hash given value using sha256.

        :return: hashed original text
        """
        pass
