"""Initializing all the existing anonymizers."""
from .anonymizer import Anonymizer
from .hash import Hash
from .mask import Mask
from .redact import Redact
from .replace import Replace

__all__ = [
    "Anonymizer",
    "Hash",
    "Mask",
    "Redact",
    "Replace"
]
