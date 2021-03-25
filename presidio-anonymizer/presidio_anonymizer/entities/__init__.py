"""Handles all the entities objects (structs) of the anonymizer."""
from .invalid_exception import InvalidParamException
from .engine import RecognizerResult


__all__ = [
    "RecognizerResult",
    "InvalidParamException"
]
