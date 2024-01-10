"""Structured Analysis module."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class StructuredAnalysis:
    """
    Dataclass containing entity analysis from structured data.

    Currently, this class only contains entity mapping.

    param entity_mapping : dict. Mapping column/key names to entity types, e.g., {
        "person.name": "PERSON",
        "person.address": "LOCATION"
        }
    """

    entity_mapping: Dict[str, str]
