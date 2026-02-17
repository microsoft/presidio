"""Routing policy helpers for multi-recognizer GLiNER pipelines."""

from __future__ import annotations

from typing import Dict, List, Tuple


def result_dedupe_key(text: str, result) -> Tuple[str, int, int, str]:
    normalized = " ".join(text[result.start : result.end].split()).lower()
    return result.entity_type, result.start, result.end, normalized


def is_gliner_result(result, free_text_name: str, dob_name: str) -> bool:
    explanation = result.analysis_explanation
    if not explanation or not explanation.recognizer:
        return False
    return explanation.recognizer in {free_text_name, dob_name}


def filter_results_by_source(
    *,
    text: str,
    results: List,
    use_source_routing: bool,
    gliner_owned_entities,
    regex_owned_entities,
    gliner_recognizer_names,
) -> List:
    if not use_source_routing:
        return results

    filtered = []
    free_text_name, dob_name = gliner_recognizer_names
    for result in results:
        result_is_gliner = is_gliner_result(result, free_text_name, dob_name)
        entity = result.entity_type
        if entity in gliner_owned_entities and not result_is_gliner:
            continue
        if entity in regex_owned_entities and result_is_gliner:
            continue
        filtered.append(result)

    best_by_key: Dict[Tuple[str, int, int, str], object] = {}
    for result in filtered:
        key = result_dedupe_key(text, result)
        best = best_by_key.get(key)
        if best is None or result.score > best.score:
            best_by_key[key] = result
    return list(best_by_key.values())
