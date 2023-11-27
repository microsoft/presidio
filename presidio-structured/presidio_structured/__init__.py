""" presidio-structured root module. """
import logging

from .analysis_builder import JsonAnalysisBuilder, TabularAnalysisBuilder
from .config import StructuredAnalysis
from .data import CsvReader, JsonDataProcessor, JsonReader, PandasDataProcessor
from .structured_engine import StructuredEngine

logging.getLogger("presidio-structured").addHandler(logging.NullHandler())

__all__ = [
    "StructuredEngine",
    "JsonAnalysisBuilder",
    "TabularAnalysisBuilder",
    "StructuredAnalysis",
    "CsvReader",
    "JsonReader",
    "PandasDataProcessor",
    "JsonDataProcessor",
]
