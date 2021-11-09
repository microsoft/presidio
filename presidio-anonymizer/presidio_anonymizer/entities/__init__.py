"""Handles all the entities objects (structs) of the anonymizer."""
from .invalid_exception import InvalidParamException
from .engine.pii_entity import PIIEntity
from .engine.operator_config import OperatorConfig
from .engine.recognizer_result import RecognizerResult
from .engine.result.engine_result import EngineResult
from .engine.result.operator_result import OperatorResult

__all__ = [
    "InvalidParamException",
    "PIIEntity",
    "OperatorConfig",
    "OperatorResult",
    "RecognizerResult",
    "EngineResult",
]
