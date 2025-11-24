"""Entity mapping and filtering utilities for LLM recognizers."""
import logging
from typing import List, Set

from presidio_analyzer import RecognizerResult

logger = logging.getLogger("presidio-analyzer")

GENERIC_PII_ENTITY = "GENERIC_PII_ENTITY"


def filter_results_by_labels(
    results: List[RecognizerResult],
    labels_to_ignore: List[str]
) -> List[RecognizerResult]:
    """Filter out results with ignored entity labels."""
    labels_to_ignore_lower = [label.lower() for label in labels_to_ignore]
    filtered = []

    for result in results:
        if not result.entity_type:
            logger.warning("LLM returned result without entity_type, skipping")
            continue

        if result.entity_type.lower() in labels_to_ignore_lower:
            logger.debug(
                "Entity %s at [%d:%d] is in labels_to_ignore, skipping",
                result.entity_type, result.start, result.end
            )
            continue

        filtered.append(result)

    return filtered


def filter_results_by_score(
    results: List[RecognizerResult],
    min_score: float
) -> List[RecognizerResult]:
    """Filter out results below minimum score threshold."""
    filtered = []

    for result in results:
        if result.score < min_score:
            logger.debug(
                "Entity %s at [%d:%d] below min_score (%.2f < %.2f), skipping",
                result.entity_type, result.start, result.end,
                result.score, min_score
            )
            continue

        filtered.append(result)

    return filtered


def filter_results_by_entities(
    results: List[RecognizerResult],
    requested_entities: List[str]
) -> List[RecognizerResult]:
    """Filter results to only include requested entity types."""
    if not requested_entities:
        return results

    filtered = []

    for result in results:
        if result.entity_type not in requested_entities:
            logger.debug(
                "Entity %s at [%d:%d] not in requested entities %s, skipping",
                result.entity_type, result.start, result.end, requested_entities
            )
            continue

        filtered.append(result)

    return filtered


def validate_result_positions(
    results: List[RecognizerResult]
) -> List[RecognizerResult]:
    """Filter out results with invalid start/end positions."""
    filtered = []

    for result in results:
        if result.start is None or result.end is None:
            logger.warning(
                "LLM returned result without start/end positions, skipping"
            )
            continue

        filtered.append(result)

    return filtered


def consolidate_generic_entities(
    results: List[RecognizerResult],
    supported_entities: List[str],
    generic_entities_logged: Set[str]
) -> List[RecognizerResult]:
    """Consolidate unmapped entities to GENERIC_PII_ENTITY."""
    processed = []

    for result in results:
        if result.entity_type not in supported_entities:
            original_entity_type = result.entity_type
            result.entity_type = GENERIC_PII_ENTITY

            if original_entity_type not in generic_entities_logged:
                logger.warning(
                    "Detected unmapped entity '%s', "
                    "consolidated to GENERIC_PII_ENTITY. "
                    "To map or exclude, update "
                    "'entity_mappings' or 'labels_to_ignore'.",
                    original_entity_type,
                )
                generic_entities_logged.add(original_entity_type)

            if result.recognition_metadata is None:
                result.recognition_metadata = {}
            result.recognition_metadata["original_entity_type"] = original_entity_type

        processed.append(result)

    return processed


def skip_unmapped_entities(
    results: List[RecognizerResult],
    supported_entities: List[str]
) -> List[RecognizerResult]:
    """Skip unmapped entities instead of consolidating."""
    filtered = []

    for result in results:
        if result.entity_type not in supported_entities:
            logger.warning(
                "Detected unmapped entity '%s', skipped "
                "(enable_generic_consolidation=False). "
                "To map or exclude, update "
                "'entity_mappings' or 'labels_to_ignore'.",
                result.entity_type,
            )
            continue

        filtered.append(result)

    return filtered


def ensure_generic_entity_support(
    supported_entities: List[str],
    enable_generic_consolidation: bool
) -> List[str]:
    """Ensure GENERIC_PII_ENTITY in supported entities if needed."""
    entities = supported_entities.copy()

    if enable_generic_consolidation and GENERIC_PII_ENTITY not in entities:
        entities.append(GENERIC_PII_ENTITY)

    return entities
