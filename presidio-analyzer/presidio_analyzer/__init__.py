"""Presidio analyzer package."""

import logging

from presidio_analyzer.presidio_logger import PresidioLogger
from presidio_analyzer.pattern import Pattern
from presidio_analyzer.analysis_explanation import AnalysisExplanation
from presidio_analyzer.recognizer_result import RecognizerResult
from presidio_analyzer.entity_recognizer import EntityRecognizer
from presidio_analyzer.local_recognizer import LocalRecognizer
from presidio_analyzer.pattern_recognizer import PatternRecognizer
from presidio_analyzer.remote_recognizer import RemoteRecognizer
from presidio_analyzer.recognizer_registry import RecognizerRegistry
from presidio_analyzer.analyzer_engine import AnalyzerEngine
from presidio_analyzer.analyzer_request import AnalyzerRequest

logging.getLogger("presidio-analyzer").addHandler(logging.NullHandler())

__all__ = [
    "PresidioLogger",
    "Pattern",
    "AnalysisExplanation",
    "RecognizerResult",
    "EntityRecognizer",
    "LocalRecognizer",
    "PatternRecognizer",
    "RemoteRecognizer",
    "RecognizerRegistry",
    "AnalyzerEngine",
    "AnalyzerRequest",
]
