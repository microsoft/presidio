"""Anonymizer root module."""
import logging

# Set up default logging (with NullHandler)

logging.getLogger("presidio-structured").addHandler(logging.NullHandler())
