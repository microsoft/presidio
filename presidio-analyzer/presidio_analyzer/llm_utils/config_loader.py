"""Configuration loading utilities for LLM recognizers."""
import logging
from typing import Dict

import yaml

logger = logging.getLogger("presidio-analyzer")


def load_yaml_config(config_path: str) -> Dict:
    """Load YAML configuration file.

    :param config_path: Path to YAML configuration file.
    :return: Parsed configuration dictionary.
    :raises FileNotFoundError: If config file doesn't exist.
    :raises ValueError: If YAML parsing fails.
    """
    try:
        with open(config_path) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse YAML configuration: {e}")


def extract_lm_config(full_config: Dict) -> Dict:
    """Extract LM recognizer settings from configuration.

    :param full_config: Full configuration dictionary.
    :return: LM recognizer configuration dictionary.
    """
    lm_config = full_config.get("lm_recognizer", {})

    # Build config for LMRecognizer __init__
    return {
        "supported_entities": lm_config.get("supported_entities"),
        "min_score": lm_config.get("min_score", 0.5),
        "labels_to_ignore": lm_config.get("labels_to_ignore", []),
        "enable_generic_consolidation": lm_config.get(
            "enable_generic_consolidation", True
        ),
    }


def get_model_config(config: Dict, provider_key: str) -> Dict:
    """Extract model-specific configuration.

    :param config: Full configuration dictionary.
    :param provider_key: Provider-specific key (e.g., "langextract", "openai").
    :return: Model configuration dictionary.
    :raises ValueError: If model configuration is missing or invalid.
    """
    provider_config = config.get(provider_key, {})
    if not provider_config:
        raise ValueError(f"Configuration must contain '{provider_key}' section")

    model_config = provider_config.get("model", {})
    if not model_config:
        raise ValueError(
            f"Configuration '{provider_key}' must contain 'model' section"
        )

    if not model_config.get("model_id"):
        raise ValueError(
            f"Configuration '{provider_key}.model' must contain 'model_id'"
        )

    return model_config
