"""Initializing all the existing anonymizers."""
from .manipulator import ManipulatorType, Manipulator
from .hash import Hash
from .mask import Mask
from .redact import Redact
from .replace import Replace
from .encrypt import Encrypt

__all__ = ["ManipulatorType", "Manipulator", "Hash", "Mask", "Redact", "Replace",
           "Encrypt"]
