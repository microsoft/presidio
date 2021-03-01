"""Handles all the entities objects (structs) of the anonymizer."""

from .invalid_exception import InvalidParamException
from .analyzer_result import AnalyzerResult
from .analyzer_results import AnalyzerResults
from .anonymizer_request import AnonymizerRequest
from .anonymized_text_builder import AnonymizedTextBuilder
from .anonymizer_config import AnonymizerConfig

__all__ = [
    "InvalidParamException",
    "AnalyzerResult",
    "AnalyzerResults",
    "AnonymizerConfig",
    "AnonymizedTextBuilder",
    "AnonymizerRequest",
]
