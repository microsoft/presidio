"""Handles all the entities objects (structs) of the anonymizer."""

from .analyzer_results import AnalyzerResults
from .invalid_exception import InvalidParamException
from .engine_request import AnonymizerRequest
from .analyzer_result import AnalyzerResult

__all__ = [
    "AnalyzerResult",
    "AnalyzerResults",
    "InvalidParamException",
    "AnonymizerRequest"
]
