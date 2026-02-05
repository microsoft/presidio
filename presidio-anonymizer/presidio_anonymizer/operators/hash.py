"""Hashes the PII text entity."""

import os
from hashlib import sha256, sha512
from typing import Dict

from presidio_anonymizer.operators import Operator, OperatorType
from presidio_anonymizer.services.validators import validate_parameter_in_range


class Hash(Operator):
    """Hash given text with sha256/sha512 algorithm."""

    HASH_TYPE = "hash_type"
    SALT = "salt"
    SHA256 = "sha256"
    SHA512 = "sha512"

    def operate(self, text: str = None, params: Dict = None) -> str:
        """
        Hash given value using sha256 or sha512 with salt.

        :param text: The text to hash
        :param params: Dictionary containing:
            - hash_type: The hash algorithm to use (sha256 or sha512)
            - salt: Optional user-provided salt for reproducible hashing.
                    If not provided, a random salt is generated per entity.
        :return: hashed original text with salt
        """
        hash_type = self._get_hash_type_or_default(params)

        # Use user-provided salt if available, otherwise generate random salt
        if self.SALT in params:
            salt = params[self.SALT]
            # Ensure salt is bytes
            if isinstance(salt, str):
                salt = salt.encode()
        else:
            # Generate random salt for this entity (prevents brute-force attacks)
            salt = os.urandom(32)

        # Concatenate text and salt before hashing
        salted_text = text.encode() + salt

        hash_switcher = {
            self.SHA256: lambda s: sha256(s),
            self.SHA512: lambda s: sha512(s),
        }
        return hash_switcher.get(hash_type)(salted_text).hexdigest()

    def validate(self, params: Dict = None) -> None:
        """Validate the hash type is string and in range of allowed hash types."""
        validate_parameter_in_range(
            [self.SHA256, self.SHA512],
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
