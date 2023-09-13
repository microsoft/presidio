""" Structured Analysis module. """

from dataclasses import dataclass
from typing import Dict


@dataclass
class StructuredAnalysis:
    """Dataclass containing entity analysis from structured data. Currently only contains entity mapping."""

    entity_mapping: Dict[
        str, str
    ]  # NOTE ideally Literal[...] with allowed EntityTypes, but cannot unpack in Literal.
