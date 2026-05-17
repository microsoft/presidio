"""Unified Pydantic configuration models for Presidio Analyzer.

This module defines the single-file configuration schema for the analyzer.
It consolidates what was previously spread across three separate files:
- ``default_analyzer.yaml`` (engine settings)
- ``default.yaml`` (NLP engine configuration)
- ``default_recognizers.yaml`` (recognizer registry)

Usage::

    from presidio_analyzer.configuration import AnalyzerConfiguration

    # Load from YAML
    config = AnalyzerConfiguration.from_yaml("analyzer.yaml")

    # Load with defaults
    config = AnalyzerConfiguration()

    # Create from dict
    config = AnalyzerConfiguration(**my_dict)
"""

import logging
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from presidio_analyzer.input_validation import (
    RecognizerRegistryConfig,
    validate_language_codes,
)
from presidio_analyzer.nlp_engine import NerModelConfiguration

logger = logging.getLogger("presidio-analyzer")


class NlpModelConfig(BaseModel):
    """Configuration for a single NLP model.

    :param lang_code: Language code (e.g., 'en', 'es').
    :param model_name: Model name or dict mapping engine names to model names.
        For spaCy/Stanza: a string (e.g., ``en_core_web_lg``).
        For Transformers: a dict (e.g.,
        ``{"spacy": "en_core_web_sm", "transformers": "model_name"}``).
    """

    lang_code: str = Field(..., description="Language code (e.g., 'en', 'es')")
    model_name: Union[str, Dict[str, str]] = Field(
        ...,
        description="Model name string or dict mapping engine to model name",
    )

    @field_validator("lang_code")
    @classmethod
    def validate_lang_code(cls, v: str) -> str:
        """Validate language code format."""
        validate_language_codes([v])
        return v


class NlpConfiguration(BaseModel):
    """NLP engine configuration.

    Defines which NLP engine and models to use for tokenization,
    lemmatization, and (optionally) NER.

    :param nlp_engine_name: Name of the NLP engine
        (``spacy``, ``stanza``, ``transformers``, or ``slim``).
    :param models: List of NLP models, one per language.
    :param ner_model_configuration: Optional NER model mapping and tuning.
    :param generic_tokenizer: Optional generic tokenizer for the slim engine.
    """

    nlp_engine_name: str = Field(
        default="spacy",
        description="NLP engine name: 'spacy', 'stanza', 'transformers', or 'slim'",
    )
    models: List[NlpModelConfig] = Field(
        default_factory=lambda: [
            NlpModelConfig(lang_code="en", model_name="en_core_web_lg")
        ],
        description="List of NLP models, one per language",
    )
    ner_model_configuration: Optional[NerModelConfiguration] = Field(
        default=None,
        description="NER model configuration for entity mapping and tuning",
    )
    generic_tokenizer: Optional[str] = Field(
        default=None,
        description="Generic tokenizer name for the slim NLP engine",
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("nlp_engine_name")
    @classmethod
    def validate_engine_name(cls, v: str) -> str:
        """Validate NLP engine name."""
        valid_engines = {"spacy", "stanza", "transformers", "slim"}
        if v not in valid_engines:
            raise ValueError(
                f"Invalid NLP engine name: '{v}'. "
                f"Must be one of: {sorted(valid_engines)}"
            )
        return v

    @field_validator("models")
    @classmethod
    def validate_models_not_empty(cls, v: List[NlpModelConfig]) -> List[NlpModelConfig]:
        """Validate at least one model is provided."""
        if not v:
            raise ValueError("At least one NLP model must be configured")
        return v

    @model_validator(mode="after")
    def validate_no_duplicate_languages(self) -> "NlpConfiguration":
        """Ensure no duplicate lang_code entries in models."""
        lang_codes = [m.lang_code for m in self.models]
        duplicates = [lc for lc in lang_codes if lang_codes.count(lc) > 1]
        if duplicates:
            raise ValueError(
                f"Duplicate lang_code entries in NLP models: "
                f"{sorted(set(duplicates))}. "
                f"Each language should have exactly one model."
            )
        return self

    def to_provider_dict(self) -> Dict[str, Any]:
        """Convert to the dict format expected by NlpEngineProvider.

        :return: Dictionary compatible with NlpEngineProvider.
        """
        result: Dict[str, Any] = {
            "nlp_engine_name": self.nlp_engine_name,
            "models": [m.model_dump() for m in self.models],
        }
        if self.ner_model_configuration:
            result["ner_model_configuration"] = self.ner_model_configuration.to_dict()
        if self.generic_tokenizer:
            result["generic_tokenizer"] = self.generic_tokenizer
        return result


class AnalyzerConfiguration(BaseModel):
    """Unified Presidio Analyzer configuration.

    Single Pydantic model that consolidates all analyzer configuration:
    engine settings, NLP configuration, and recognizer registry.

    :param supported_languages: Languages the analyzer supports.
    :param default_score_threshold: Minimum confidence score (0.0–1.0)
        for returning results.
    :param nlp_configuration: NLP engine and model configuration.
    :param recognizer_registry: Recognizer registry configuration
        (recognizers, regex flags).

    Example YAML::

        supported_languages:
          - en

        default_score_threshold: 0.0

        nlp_configuration:
          nlp_engine_name: spacy
          models:
            - lang_code: en
              model_name: en_core_web_lg

        recognizer_registry:
          global_regex_flags: 26
          recognizers:
            - name: CreditCardRecognizer
              type: predefined
    """

    supported_languages: List[str] = Field(
        default=["en"],
        description="Languages supported by this analyzer instance",
    )
    default_score_threshold: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score for entity detection",
    )
    nlp_configuration: Optional[NlpConfiguration] = Field(
        default=None,
        description="NLP engine and model configuration",
    )
    recognizer_registry: Optional[RecognizerRegistryConfig] = Field(
        default=None,
        description="Recognizer registry configuration",
    )

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    @model_validator(mode="before")
    @classmethod
    def propagate_languages_to_registry(cls, data: Any) -> Any:
        """Inject supported_languages into recognizer_registry if missing.

        The top-level ``supported_languages`` applies to the entire analyzer,
        including the recognizer registry.  When the registry section omits
        ``supported_languages``, copy the top-level value so that recognizer
        validation sees the correct language list.
        """
        if isinstance(data, dict):
            languages = data.get("supported_languages")
            registry = data.get("recognizer_registry")
            if (
                isinstance(registry, dict)
                and "supported_languages" not in registry
                and languages
            ):
                registry["supported_languages"] = languages
        return data

    @field_validator("supported_languages")
    @classmethod
    def validate_languages(cls, v: List[str]) -> List[str]:
        """Validate language code formats."""
        if not v:
            raise ValueError("At least one supported language must be specified")
        validate_language_codes(v)
        return v

    @model_validator(mode="after")
    def validate_nlp_covers_languages(self) -> "AnalyzerConfiguration":
        """Warn if NLP models don't cover all supported languages."""
        if self.nlp_configuration and self.nlp_configuration.models:
            nlp_langs = {m.lang_code for m in self.nlp_configuration.models}
            configured_langs = set(self.supported_languages)
            missing = configured_langs - nlp_langs
            if missing:
                logger.warning(
                    f"NLP models do not cover all supported languages. "
                    f"Missing: {sorted(missing)}. "
                    f"Configured NLP languages: {sorted(nlp_langs)}. "
                    f"Analysis for these languages will not use NLP features."
                )
        return self

    @classmethod
    def from_yaml(cls, file_path: Union[str, Path]) -> "AnalyzerConfiguration":
        """Load and validate configuration from a YAML file.

        :param file_path: Path to the YAML configuration file.
        :return: Validated AnalyzerConfiguration instance.
        :raises FileNotFoundError: If the file does not exist.
        :raises ValueError: If the YAML content is invalid.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")

        try:
            with open(path) as f:
                raw = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file {path}: {e}") from e

        if raw is None:
            raise ValueError(f"Configuration file is empty: {path}")
        if not isinstance(raw, dict):
            raise ValueError(
                f"Configuration file must contain a YAML mapping, "
                f"got {type(raw).__name__}: {path}"
            )

        # Detect and warn about deprecated separate-file format keys
        deprecated_top_keys = {"nlp_engine_name", "models"}
        found_deprecated = deprecated_top_keys & set(raw.keys())
        if found_deprecated:
            warnings.warn(
                f"Configuration file '{path}' appears to use the deprecated "
                f"standalone NLP configuration format "
                f"(found top-level keys: {sorted(found_deprecated)}). "
                f"Please migrate to the unified analyzer configuration format. "
                f"See: https://microsoft.github.io/presidio/analyzer/"
                f"analyzer_engine_provider/",
                DeprecationWarning,
                stacklevel=2,
            )

        try:
            return cls(**raw)
        except ValidationError as e:
            raise ValueError(f"Invalid analyzer configuration in {path}") from e

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "AnalyzerConfiguration":
        """Create configuration from a dictionary.

        :param config: Configuration dictionary.
        :return: Validated AnalyzerConfiguration instance.
        """
        return cls(**config)

    @staticmethod
    def get_default_conf_path() -> Path:
        """Return the path to the default unified configuration file.

        :return: Path to ``conf/analyzer.yaml``.
        """
        return Path(Path(__file__).parent, "../conf", "analyzer.yaml")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize configuration to a dictionary.

        :return: Dictionary representation of the configuration.
        """
        return self.model_dump(exclude_none=True)
