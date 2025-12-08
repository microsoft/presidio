"""Analyzer mode definitions for pre-configured analyzer setups."""

import logging
from enum import Enum
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger("presidio-analyzer")

# Base path for mode configurations
MODES_CONF_DIR = Path(__file__).parent / "conf" / "modes"


class AnalyzerMode(Enum):
    """
    Pre-configured analyzer modes for common use cases.

    - FAST: spaCy with small model, lowest latency (~5-10ms)
    - BALANCED: Transformers NER, good accuracy/speed trade-off (~50-100ms)
    - ACCURATE: Transformers + Ollama LLM, maximum accuracy (~200-500ms)
    - CUSTOM: User provides their own configuration
    """

    FAST = "fast"
    BALANCED = "balanced"
    ACCURATE = "accurate"
    CUSTOM = "custom"


def get_mode_config_dir(mode: AnalyzerMode) -> Path:
    """Get the configuration directory for a mode."""
    if mode == AnalyzerMode.CUSTOM:
        raise ValueError(
            "CUSTOM mode requires a user-provided config path. "
            "Use get_custom_config_path() instead."
        )
    return MODES_CONF_DIR / mode.value


# NLP engine config filenames per mode
_NLP_ENGINE_CONFIG_FILES = {
    AnalyzerMode.FAST: "spacy.yaml",
    AnalyzerMode.BALANCED: "transformers.yaml",
    AnalyzerMode.ACCURATE: "transformers.yaml",
}


def get_nlp_engine_config(mode: AnalyzerMode) -> Path:
    """Get the NLP engine config file path for a mode."""
    config_dir = get_mode_config_dir(mode)
    config_filename = _NLP_ENGINE_CONFIG_FILES.get(mode, "spacy.yaml")
    config_file = config_dir / config_filename
    if not config_file.exists():
        raise FileNotFoundError(f"NLP config not found: {config_file}")
    return config_file


def get_recognizers_config(mode: AnalyzerMode) -> Optional[Path]:
    """Get the recognizers config file path for a mode, if it exists."""
    config_dir = get_mode_config_dir(mode)
    recognizers_config = config_dir / "recognizers.yaml"
    return recognizers_config if recognizers_config.exists() else None


def get_slm_config(mode: AnalyzerMode) -> Optional[Path]:
    """Get the SLM (Small Language Model) config file path for a mode, if it exists."""
    config_dir = get_mode_config_dir(mode)
    slm_config = config_dir / "slm.yaml"
    return slm_config if slm_config.exists() else None


def get_custom_config_path(config_path: Union[Path, str]) -> Path:
    """Validate and return custom config path."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Custom config not found: {config_path}")
    return path

