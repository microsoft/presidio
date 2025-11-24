"""Configuration loading utilities for LLM recognizers."""
import logging
from pathlib import Path
from typing import Dict, List, Union

import yaml

logger = logging.getLogger("presidio-analyzer")


def get_conf_path(filename: str, conf_subdir: str = "conf") -> Path:
    """Get absolute path to file in conf directory."""
    return Path(__file__).parent.parent / conf_subdir / filename


def load_yaml_file(filepath: Union[str, Path]) -> Dict:
    """Load and parse a YAML file.

    :param filepath: Path to YAML file (absolute or relative).
    :return: Parsed YAML data.
    :raises FileNotFoundError: If file doesn't exist.
    :raises ValueError: If YAML parsing fails.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        with open(filepath) as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse YAML: {e}")


def get_model_config(config: Dict, provider_key: str) -> Dict:
    """Extract model configuration for specific provider."""
    validate_config_fields(
        config,
        [
            (provider_key,),
            (provider_key, "model"),
            (provider_key, "model", "model_id"),
        ]
    )

    return config[provider_key]["model"]


def validate_config_fields(
    config: Dict,
    required_fields: List[Union[str, tuple]],
    config_name: str = "Configuration"
) -> None:
    """Validate that required fields exist in configuration.

    :param config: Configuration dictionary to validate.
    :param required_fields: List of required field paths. Can be:
        - str: Simple key like "model_id"
        - tuple: Nested path like ("langextract", "model", "model_id")
    :param config_name: Name of configuration for error messages.
    :raises ValueError: If any required field is missing.

    Example:
        validate_config_fields(
            config,
            [
                ("langextract", "model", "model_id"),
                ("langextract", "entity_mappings"),
                "supported_entities"
            ]
        )
    """
    for field in required_fields:
        if isinstance(field, str):
            if not config.get(field):
                raise ValueError(f"{config_name} must contain '{field}'")
        elif isinstance(field, tuple):
            current = config
            for i, key in enumerate(field):
                if not isinstance(current, dict) or key not in current:
                    path = ".".join(field[:i+1])
                    raise ValueError(f"{config_name} must contain '{path}'")
                current = current[key]
                if i == len(field) - 1 and not current:
                    path = ".".join(field)
                    raise ValueError(f"{config_name} must contain '{path}'")
