"""Utilities for LLM-based recognizers."""

from .config_loader import (
    get_conf_path,
    get_model_config,
    load_yaml_file,
    validate_config_fields,
)
from .entity_mapper import (
    GENERIC_PII_ENTITY,
    consolidate_generic_entities,
    ensure_generic_entity_support,
    filter_results_by_entities,
    filter_results_by_labels,
    filter_results_by_score,
    skip_unmapped_entities,
    validate_result_positions,
)
from .examples_loader import (
    convert_to_langextract_format,
    load_yaml_examples,
)
from .langextract_helper import (
    DEFAULT_ALIGNMENT_SCORES,
    calculate_extraction_confidence,
    create_reverse_entity_mapping,
    extract_lm_config,
    get_langextract_module,
    get_supported_entities,
)
from .prompt_loader import (
    load_file_from_conf,
    load_prompt_file,
    render_jinja_template,
)

__all__ = [
    # File and path utilities
    "get_conf_path",
    "load_file_from_conf",
    "load_prompt_file",
    # YAML utilities
    "load_yaml_file",
    "load_yaml_examples",
    # LangExtract utilities
    "get_langextract_module",
    "extract_lm_config",
    "get_supported_entities",
    "create_reverse_entity_mapping",
    "calculate_extraction_confidence",
    "DEFAULT_ALIGNMENT_SCORES",
    # Entity mapping and filtering
    "GENERIC_PII_ENTITY",
    "filter_results_by_labels",
    "filter_results_by_score",
    "filter_results_by_entities",
    "validate_result_positions",
    "consolidate_generic_entities",
    "skip_unmapped_entities",
    "ensure_generic_entity_support",
    # Config extraction and validation
    "get_model_config",
    "validate_config_fields",
    # Template rendering
    "render_jinja_template",
    # Format conversion
    "convert_to_langextract_format",
]
