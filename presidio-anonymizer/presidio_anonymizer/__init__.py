"""Anonymizer root module."""
import logging

from .anonymizer_engine import AnonymizerEngine
from .deanonymize_engine import DeanonymizeEngine
from .batch_anonymizer_engine import BatchAnonymizerEngine
from .entities import (
    InvalidParamException,
    ConflictResolutionStrategy,
    PIIEntity,
    OperatorConfig,
    OperatorResult,
    RecognizerResult,
    EngineResult,
    DictRecognizerResult,
)

# Set up default logging (with NullHandler)


logging.getLogger("presidio-anonymizer").addHandler(logging.NullHandler())

__all__ = [
    "AnonymizerEngine",
    "DeanonymizeEngine",
    "BatchAnonymizerEngine",
    "InvalidParamException",
    "ConflictResolutionStrategy",
    "PIIEntity",
    "OperatorConfig",
    "OperatorResult",
    "RecognizerResult",
    "EngineResult",
    "DictRecognizerResult",
]
