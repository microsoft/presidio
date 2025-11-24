"""LangExtract helper utilities."""
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    pass


# Default alignment score mappings for LangExtract extractions
DEFAULT_ALIGNMENT_SCORES = {
    "MATCH_EXACT": 0.95,
    "MATCH_FUZZY": 0.80,
    "MATCH_LESSER": 0.70,
    "NOT_ALIGNED": 0.60,
}


def get_langextract_module():
    """Get langextract module or raise ImportError with install instructions."""
    try:
        import langextract as lx
        return lx
    except ImportError:
        raise ImportError(
            "LangExtract is not installed. "
            "Install it with: poetry install --extras langextract"
        )


def extract_lm_config(config: Dict) -> Dict:
    """Extract LM recognizer configuration with defaults."""
    lm_config_section = config.get("lm_recognizer", {})

    return {
        "supported_entities": lm_config_section.get("supported_entities"),
        "min_score": lm_config_section.get("min_score", 0.5),
        "labels_to_ignore": lm_config_section.get("labels_to_ignore", []),
        "enable_generic_consolidation": lm_config_section.get(
            "enable_generic_consolidation", True
        ),
    }


def get_supported_entities(
    lm_config: Dict,
    langextract_config: Dict
) -> Optional[List[str]]:
    """Get supported entities from either config section."""
    return (
        lm_config.get("supported_entities")
        or langextract_config.get("supported_entities")
    )


def create_reverse_entity_mapping(entity_mappings: Dict) -> Dict:
    """Create reverse mapping from Presidio entities to LangExtract classes."""
    return {v: k for k, v in entity_mappings.items()}


def calculate_extraction_confidence(
    extraction,
    alignment_scores: Optional[Dict[str, float]] = None
) -> float:
    """Calculate confidence score from LangExtract extraction.

    :param extraction: LangExtract extraction object.
    :param alignment_scores: Custom alignment score mappings. If None, uses defaults.
    :return: Confidence score between 0 and 1.
    """
    default_score = 0.85

    if alignment_scores is None:
        alignment_scores = DEFAULT_ALIGNMENT_SCORES

    if not hasattr(extraction, "alignment_status") or not (
        extraction.alignment_status
    ):
        return default_score

    status = str(extraction.alignment_status).upper()
    for status_key, score in alignment_scores.items():
        if status_key in status:
            return score

    return default_score
