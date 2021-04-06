"""Initializing all the existing anonymizers."""
from .operator import OperatorType, Operator
from .hash import Hash
from .mask import Mask
from .redact import Redact
from .replace import Replace
from .encrypt import Encrypt
from .decrypt import Decrypt
from .operators_factory import OperatorsFactory

__all__ = ["OperatorType",
           "Operator",
           "Hash",
           "Mask",
           "Redact",
           "Replace",
           "Encrypt",
           "Decrypt",
           "OperatorsFactory"]
