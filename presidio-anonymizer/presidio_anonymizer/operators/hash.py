"""Hashes the PII text entity."""
from hashlib import sha256, sha512, md5
from typing import Dict

from presidio_anonymizer.operators import Operator, OperatorType
from presidio_anonymizer.services.validators import validate_parameter_in_range


class Hash(Operator):
    """Hash given text with sha256/sha512/md5 algorithm."""

    HASH_TYPE = "hash_type"
    SHA256 = "sha256"
    SHA512 = "sha512"
    MD5 = "md5"

    def operate(self, text: str = None, params: Dict = None) -> str:
        """
        Hash given value using sha256.

        :return: hashed original text
        """
        hash_type = self._get_hash_type_or_default(params)
        hash_switcher = {
            self.SHA256: lambda s: sha256(s),
            self.SHA512: lambda s: sha512(s),
            self.MD5: lambda s: md5(s),
        }
        return hash_switcher.get(hash_type)(text.encode()).hexdigest()

    def validate(self, params: Dict = None) -> None:
        """Validate the hash type is string and in range of allowed hash types."""
        validate_parameter_in_range(
            [self.SHA256, self.SHA512, self.MD5],
            self._get_hash_type_or_default(params),
            self.HASH_TYPE,
            str,
        )
        pass

    def operator_name(self) -> str:
        """Return operator name."""
        return "hash"

    def _get_hash_type_or_default(self, params: Dict = None):
        return params.get(self.HASH_TYPE, self.SHA256)

    def operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.Anonymize
