"""Handles all the domain objects (structs) of the anonymizer."""
from .anonymizer_request import AnonymizerRequest
from .analyzer_result import AnalyzerResult

from .analyzer_results import AnalyzerResults
from .invalid_exception import InvalidParamException

__all__ = [
    "AnonymizerRequest",
    "AnalyzerResult",
    "AnalyzerResults",
    "InvalidParamException"
]
