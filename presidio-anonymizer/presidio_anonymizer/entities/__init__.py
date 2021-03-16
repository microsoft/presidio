"""Handles all the entities objects (structs) of the anonymizer."""

from .invalid_exception import InvalidParamException
from presidio_anonymizer.entities.engine.recognizer_result import RecognizerResult
from presidio_anonymizer.entities.engine.anonymizer_config import AnonymizerConfig

__all__ = [
    "InvalidParamException",
    "RecognizerResult",
    "AnonymizerConfig",
]
