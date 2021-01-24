"""Initializing all the existing anonymizers."""
from .anonymizer import Anonymizer
from .fpe import FPE
from .hash import Hash
from .mask import Mask
from .redact import Redact
from .replace import Replace

__all__ = [
    "Anonymizer",
    "FPE",
    "Hash",
    "Mask",
    "Redact",
    "Replace"
]
