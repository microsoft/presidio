"""Handles all the entities objects (structs) of the anonymizer."""

from .invalid_exception import InvalidParamException
from .analyzer_result import AnalyzerResult
from .analyzer_results import AnalyzerResults
from .anonymizer_request import AnonymizerRequest
from .text_manipulator import AnonymizedTextBuilder

__all__ = [
    "InvalidParamException",
    "AnalyzerResult",
    "AnalyzerResults",
    "AnonymizerRequest",
    "AnonymizedTextBuilder",
]
