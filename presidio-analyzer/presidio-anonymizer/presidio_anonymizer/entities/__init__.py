"""Handles all the entities objects (structs) of the anonymizer."""

from .invalid_exception import InvalidParamError  # isort:skip
from .conflict_resolution_strategy import ConflictResolutionStrategy
from .engine.operator_config import OperatorConfig
from .engine.pii_entity import PIIEntity
from .engine.recognizer_result import RecognizerResult
from .engine.result.engine_result import EngineResult
from .engine.result.operator_result import OperatorResult

from .engine.dict_recognizer_result import DictRecognizerResult  # isort: skip

__all__ = [
    "InvalidParamError",
    "ConflictResolutionStrategy",
    "PIIEntity",
    "OperatorConfig",
    "OperatorResult",
    "RecognizerResult",
    "EngineResult",
    "DictRecognizerResult",
]
