"""Handles all the entities objects (structs) of the anonymizer."""
from .invalid_exception import InvalidParamException
from .pii_entity import PIIEntity
from .operator_config import OperatorConfig
from .operator_result import OperatorResult
from .recognizer_result import RecognizerResult
from .anonymizer_result import AnonymizerResult
from .engine_result import EngineResult

__all__ = [
    "InvalidParamException",
    "PIIEntity",
    "OperatorConfig",
    "OperatorResult",
    "RecognizerResult",
    "AnonymizerResult",
    "EngineResult",
]
