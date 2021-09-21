from typing import Dict

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.operators import Operator, OperatorType
from presidio_anonymizer.operators.aes_cipher import AESCipher
from presidio_anonymizer.services.validators import validate_parameter
from presidio_anonymizer.operators.ff3_1_cipher import FPEFF31Cipher


def format_align_digits(text, reference_text):
    """
    reformat digits  in text to align with non-digit separators for refence format.

    :param text: text to format
    :param reference_text: formatting reference
    """
    if len(text) != len(reference_text):
        for idx, t in enumerate(reference_text):
            if not t.isdigit():
                text = text[:idx] + reference_text[idx] + text[idx:]
    return text


class Encrypt(Operator):
    """Anonymizes text to an encrypted form, or it to be restored using decrypted."""

    KEY = "key"
    ENCRYPTION_METHOD = "encryption"
    FPE_TWEAK = "tweak"
    RADIX = "radix"

    def operate(self, text: str = None, params: Dict = None) -> str:
        """
        Anonymize the text with an encrypted text.

        :param text: The text for encryption.
        :param params:
            * *key* The key supplied by the user for the encryption.
        :return: The encrypted text
        """
        encoded_key = params.get(self.KEY).encode("utf8")
        encryption_method = params.get(self.ENCRYPTION_METHOD)
        encrypted_text = None
        if encryption_method == "FPEFF31":
            fpe_tweak = params.get(self.FPE_TWEAK).encode("utf8")
            radix = params.get(self.RADIX, 64)
            text_scrubbed: str = None
            if radix == 10:
                text_scrubbed = "".join(t for t in text if t.isdigit())
                encrypted_text: str = \
                    FPEFF31Cipher.encrypt(encoded_key, fpe_tweak, text_scrubbed, radix)
                encrypted_text = format_align_digits(encrypted_text, text)
            else:
                encrypted_text: str = \
                    FPEFF31Cipher.encrypt(encoded_key, fpe_tweak, text, radix)

        else:
            encrypted_text = AESCipher.encrypt(encoded_key, text)
        return encrypted_text

    def validate(self, params: Dict = None) -> None:
        """
        Validate Encrypt parameters.

        :param params:
            * *key* The key supplied by the user for the encryption.
                    Should be a string of 128, 192 or 256 bits length.
        :raises InvalidParamException in case on an invalid parameter.
        """
        key = params.get(self.KEY)
        validate_parameter(key, self.KEY, str)
        if not AESCipher.is_valid_key_size(key.encode("utf8")):
            raise InvalidParamException(
                f"Invalid input, {self.KEY} must be of length 128, 192 or 256 bits"
            )

    def operator_name(self) -> str:
        """Return operator name."""
        return "encrypt"

    def operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.Anonymize
