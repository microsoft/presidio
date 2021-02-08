"""Presidio analyzer package."""

import logging

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

# Define default loggers behavior

# 1. presidio_analyzer logger

logging.getLogger("presidio-analyzer").addHandler(logging.NullHandler())

# 2. decision_process logger.
# Setting the decision process trace here as we would want it
# to be activated using a parameter to AnalyzeEngine and not by default.

decision_process_logger = logging.getLogger("decision_process")
ch = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s]%(message)s")
ch.setFormatter(formatter)
decision_process_logger.addHandler(ch)
decision_process_logger.setLevel("INFO")
__all__ = [
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
