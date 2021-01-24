"""Anonymizer root module."""
import logging

from presidio_anonymizer.anonymizer_engine import AnonymizerEngine

logging.getLogger("presidio-anonymizer").addHandler(logging.NullHandler())

__all__ = ["AnonymizerEngine"]
