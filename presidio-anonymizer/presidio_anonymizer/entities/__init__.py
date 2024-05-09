"""Handles all the entities objects (structs) of the anonymizer."""

from .conflict_resolution_strategy import ConflictResolutionStrategy
from .engine.dict_recognizer_result import DictRecognizerResult
from .engine.operator_config import OperatorConfig
from .engine.pii_entity import PIIEntity
from .engine.recognizer_result import RecognizerResult
from .engine.result.engine_result import EngineResult
from .engine.result.operator_result import OperatorResult
from .invalid_exception import InvalidParamException

__all__ = [
    "InvalidParamException",
    "ConflictResolutionStrategy",
    "PIIEntity",
    "OperatorConfig",
    "OperatorResult",
    "RecognizerResult",
    "EngineResult",
    "DictRecognizerResult",
]
