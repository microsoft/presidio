"""Postprocessing helpers for GLiNER edge profile."""

from __future__ import annotations

from typing import List, Optional, Set


def filter_by_target_entities(results: List, target_entities: Optional[List[str]]) -> List:
    if not target_entities:
        return results

    allowed: Set[str] = set(target_entities)
    return [result for result in results if result.entity_type in allowed]
