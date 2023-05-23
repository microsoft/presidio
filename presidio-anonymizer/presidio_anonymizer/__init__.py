"""Anonymizer root module."""
import logging

from .anonymizer_engine import AnonymizerEngine
from .deanonymize_engine import DeanonymizeEngine
from .batch_anonymizer_engine import BatchAnonymizerEngine

# Set up default logging (with NullHandler)


logging.getLogger("presidio-anonymizer").addHandler(logging.NullHandler())

__all__ = ["AnonymizerEngine", "DeanonymizeEngine", "BatchAnonymizerEngine"]
