"""Anonymizer root module."""
import logging

from .anonymize_engine import AnonymizeEngine
from .decrypt_engine import DecryptEngine

# Set up default logging (with NullHandler)


logging.getLogger("presidio-anonymizer").addHandler(logging.NullHandler())

__all__ = ["AnonymizeEngine", "DecryptEngine"]
