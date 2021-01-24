"""Hashes the PII text entity."""


class Hash(object):
    # TODO implement + test
    """Hash given text with sha256 algorithm."""

    def anonymize(self, params={}):
        """
        Hash given value using sha256.

        :return: hashed original text
        """
        return params.get("old_text")
