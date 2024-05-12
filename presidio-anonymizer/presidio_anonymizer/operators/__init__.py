"""Initializing all the existing anonymizers."""

from .operator import OperatorType, Operator  # isort:skip
from .aes_cipher import AESCipher
from .custom import Custom
from .deanonymize_keep import DeanonymizeKeep
from .encrypt import Encrypt

from .decrypt import Decrypt  # isort:skip
from .hash import Hash
from .keep import Keep
from .mask import Mask
from .redact import Redact
from .replace import Replace

from .operators_factory import OperatorsFactory  # isort:skip

__all__ = [
    "OperatorType",
    "Operator",
    "Hash",
    "Mask",
    "Redact",
    "Keep",
    "DeanonymizeKeep",
    "Replace",
    "Custom",
    "Encrypt",
    "Decrypt",
    "AESCipher",
    "OperatorsFactory",
]
