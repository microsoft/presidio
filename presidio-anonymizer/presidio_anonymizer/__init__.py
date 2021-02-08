"""Anonymizer root module."""
import logging

from presidio_anonymizer.anonymizer_engine import AnonymizerEngine

# Set up default logging (with NullHandler)
logging.getLogger("presidio-anonymizer").addHandler(logging.NullHandler())

__all__ = ["AnonymizerEngine"]
