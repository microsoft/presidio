"""A Python CLI for analyzing PII Entities with Microsoft Presidio framework."""

import importlib.metadata

__version__ = importlib.metadata.version("presidio-cli")

APP_DESCRIPTION = __doc__
SHELL_NAME = "presidio"

APP_VERSION = __version__
