"""Anonymizer root module."""
import logging

# Set up default logging (with NullHandler)


logging.getLogger("presidio-str").addHandler(logging.NullHandler())

# __all__ = ["AnonymizerEngine", "DeanonymizeEngine", "BatchAnonymizerEngine"]
