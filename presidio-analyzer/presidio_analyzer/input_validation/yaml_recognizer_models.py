"""Pydantic models for YAML recognizer configurations."""

import logging
from typing import Any, Dict, List, Optional, Union

import regex as re
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

logger = logging.getLogger("presidio-analyzer")


class LanguageContextConfig(BaseModel):
    """Configuration for language-specific validation with context words.

    :param language: Language code (e.g., 'en', 'es')
    :param context: Context words for this language
    """

    language: str = Field(..., description="Language code (e.g., 'en', 'es')")
    context: Optional[List[str]] = Field(
        default=None, description="Context words for this language"
    )

    @field_validator("language")
    @classmethod
    def validate_language_code(cls, v: str) -> str:
        """Validate language code format."""
        if not re.match(r"^[a-z]{2}(-[A-Z]{2})?$", v):
            raise ValueError(
                f"Invalid language code format: {v}. Expected format: 'en' or 'en-US'"
            )
        return v


class BaseRecognizerConfig(BaseModel):
    """Base validation for all recognizer configuration types.

    :param name: Name of the recognizer
    :param enabled: Whether the recognizer is enabled
    :param type: Type of recognizer (predefined/custom)
    :param supported_language: Single supported language (legacy)
    :param supported_languages: Multiple supported languages with optional context.
    Passing multiple languages will result in multiple actual
    recognizers initialized in Presidio.
    :param context: context words. Context is best defined
    in the language-specific configuration,
    as it is language-dependent. If context is defined outside,
    it should only work if the user passed one language
    (either in supported_language or have a supported_languages with length 1).
    :param supported_entity: Supported entity for this recognizer (legacy)
    :param supported_entities: List of supported entities for this recognizer.
    """

    name: str = Field(..., description="Name of the recognizer")
    enabled: bool = Field(default=True, description="Whether the recognizer is enabled")
    type: Optional[str] = Field(
        default="predefined", description="Type of recognizer (predefined/custom)"
    )
    supported_language: Optional[str] = Field(
        default=None, description="The language this recognizer supports"
    )
    supported_languages: Optional[Union[List[str], List[LanguageContextConfig]]] = (
        Field(
            default=None,
            description="Multiple supported languages with optional context",
        )
    )
    context: Optional[List[str]] = Field(
        default=None, description="Global context words"
    )
    supported_entity: Optional[str] = Field(
        default=None, description="Supported entity for this recognizer"
    )
    supported_entities: Optional[List[str]] = Field(
        default=None, description="List of supported entities " "for this recognizer"
    )

    @field_validator("supported_language")
    @classmethod
    def validate_single_language(cls, v: Optional[str]) -> Optional[str]:
        """Validate single language code format."""
        if v and not re.match(r"^[a-z]{2}(-[A-Z]{2})?$", v):
            raise ValueError(f"Invalid language code format: {v}")
        return v

    @model_validator(mode="after")
    def validate_language_configuration(self):
        """Ensure proper language validation."""
        if self.supported_language and self.supported_languages:
            raise ValueError(
                "Cannot specify both 'supported_language' and 'supported_languages'"
            )

        # If neither is specified, this is allowed for
        # predefined recognizers (defaults will be used)
        return self

    @model_validator(mode="after")
    def validate_entity_configuration(self):
        """Ensure proper entity validation."""
        # Check if user provided both (before we modify them)
        user_provided_both = (
            self.supported_entity is not None and self.supported_entities is not None
        )

        if user_provided_both:
            raise ValueError(
                f"Recognizer {self.name} has both "
                "'supported_entity' and 'supported_entities' specified."
            )

        return self

    @model_validator(mode="after")
    def validate_context_configuration(self):
        """Validate context configuration according to language settings."""
        # Check if global context is defined
        if self.context:
            # Global context is only valid if we have exactly one language
            if self.supported_languages and len(self.supported_languages) > 1:
                raise ValueError(
                    "Global context can only be used with a single language. "
                    "For multiple languages, define context in "
                    "language-specific configurations."
                    "Example: "
                    "    supported_languages: "
                    "    - language: en "
                    "      context: [credit, card, visa, mastercard] "
                    "    - language: es "
                    "      context: [tarjeta, credito, visa, mastercard] "
                )
        return self


class PredefinedRecognizerConfig(BaseRecognizerConfig):
    """Configuration for predefined recognizers."""

    type: str = Field(default="predefined", description="Type of recognizer")

    @model_validator(mode="after")
    def validate_predefined_recognizer_exists(self):
        """Validate that the predefined recognizer class actually exists."""
        try:
            # Lazy import to avoid circular dependency
            from presidio_analyzer.recognizer_registry.recognizers_loader_utils import (
                RecognizerListLoader,
            )

            RecognizerListLoader.get_existing_recognizer_cls(self.name)
        except (ImportError, ModuleNotFoundError):
            return self
        except ValueError as e:
            available_recognizers = [
                cls.__name__
                for cls in RecognizerListLoader.get_all_existing_recognizers()
            ]
            raise ValueError(
                f"Predefined recognizer '{self.name}' not found. "
                f"Available predefined recognizers: "
                f"{', '.join(sorted(available_recognizers))}"
            ) from e
        return self


class CustomRecognizerConfig(BaseRecognizerConfig):
    """Configuration for custom pattern-based recognizers."""

    type: str = Field(default="custom", description="Type of recognizer")
    supported_entity: str = Field(
        ..., description="Entity type this recognizer detects"
    )
    patterns: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="List of patterns"
    )
    context: Optional[List[str]] = Field(
        default=None, description="Global context words"
    )
    deny_list: Optional[List[str]] = Field(
        default=None, description="Words to deny/exclude"
    )
    deny_list_score: Optional[float] = Field(
        default=0.0, ge=0.0, le=1.0, description="Deny list score"
    )

    # Language validation (legacy and new formats)
    supported_language: Optional[str] = Field(
        default=None, description="Single supported language (legacy)"
    )
    supported_languages: Optional[Union[List[str], List[LanguageContextConfig]]] = (
        Field(
            default=None,
            description="Multiple supported languages with optional context",
        )
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("patterns")
    @classmethod
    def validate_patterns(cls, patterns: Optional[List[Dict]]) -> Optional[List[Dict]]:
        """Validate single language code format."""
        if patterns and not isinstance(patterns, list):
            raise ValueError(f"Patterns should be a list: {patterns}")

        for pattern in patterns:
            if not isinstance(pattern, dict):
                raise ValueError(f"Pattern should be a dict: {pattern}")
            if "name" not in pattern:
                raise ValueError(f"Pattern should contain a name field: {pattern}")
            if "regex" not in pattern:
                raise ValueError(f"Pattern should contain a regex field: {pattern}")
            if "score" not in pattern:
                raise ValueError(f"Pattern should contain a score field: {pattern}")
            if not isinstance(pattern["score"], (int, float)):
                raise ValueError(f"Pattern score should be a float: {pattern}")
            if not (0.0 <= pattern["score"] <= 1.0):
                raise ValueError(f"Pattern score should be between 0 and 1: {pattern}")
        return patterns

    @field_validator("supported_language")
    @classmethod
    def validate_single_language(cls, v: Optional[str]) -> Optional[str]:
        """Validate single language code format."""
        if v and not re.match(r"^[a-z]{2}(-[A-Z]{2})?$", v):
            raise ValueError(f"Invalid language code format: {v}")
        return v

    @model_validator(mode="after")
    def validate_configuration(self):
        """Ensure configuration is valid."""
        # Check if user accidentally marked a predefined recognizer as custom
        try:
            # Lazy import to avoid circular dependency
            from presidio_analyzer.recognizer_registry.recognizers_loader_utils import (
                RecognizerListLoader,
            )

            try:
                RecognizerListLoader.get_existing_recognizer_cls(self.name)
                raise ValueError(
                    f"Recognizer '{self.name}' is a predefined recognizer "
                    f"but is marked as 'custom'. "
                    f"Either use type: 'predefined' or choose a different "
                    f"name for your custom recognizer."
                )
            except ValueError as e:
                if "was not found" not in str(e):
                    raise
        except (ImportError, ModuleNotFoundError):
            pass

        # Validate patterns or deny_list
        if not self.patterns and not self.deny_list:
            raise ValueError(
                "Custom recognizer must have at least one "
                "of 'patterns' or 'deny_list'"
            )
        return self


class RecognizerRegistryConfig(BaseModel):
    """Complete validation for the recognizer registry."""

    supported_languages: Optional[List[str]] = Field(
        default=None, description="List of supported languages"
    )
    global_regex_flags: int = Field(default=26, description="Global regex flags")
    recognizers: List[
        Union[PredefinedRecognizerConfig, CustomRecognizerConfig, str]
    ] = Field(default_factory=list, description="List of recognizer configurations")

    @field_validator("supported_languages")
    @classmethod
    def validate_language_codes(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate language codes format."""

        # Allow None or empty list for cases where languages will be inferred
        if v is None:
            return None

        if len(v) == 0:
            return []

        for lang in v:
            if not re.match(r"^[a-z]{2}(-[A-Z]{2})?$", lang):
                raise ValueError(f"Invalid language code format: {lang}")
        return v

    @model_validator(mode="after")
    def validate_languages_for_custom_recognizers(self):
        """Validate that custom recognizers have language configuration."""
        # If we have custom recognizers, we need language configuration somewhere
        for recognizer in self.recognizers:
            if isinstance(recognizer, CustomRecognizerConfig):
                # Check if this custom recognizer has its own language config
                if (
                    not recognizer.supported_language
                    and not recognizer.supported_languages
                ):
                    # If no language config on recognizer, we need global languages
                    if not self.supported_languages:
                        raise ValueError(
                            f"Language configuration missing for custom recognizer "
                            f"'{recognizer.name}': "
                            "Either specify 'supported_languages' "
                            "on the recognizer or provide "
                            "global 'supported_languages' in the "
                            "registry configuration."
                        )

        return self

    @field_validator("global_regex_flags")
    @classmethod
    def validate_global_regex_flags(cls, v: int) -> int:
        """Validate global_regex_flags and warn if using default."""
        return v

    @field_validator("recognizers", mode="before")
    @classmethod
    def parse_recognizers(cls, v):
        """Parse recognizers from various input formats without duplication."""
        if v is None:
            raise ValueError(
                "Configuration error: 'recognizers' is required. "
                "Please provide a list of recognizers in the configuration."
            )

        if not isinstance(v, list):
            raise ValueError("Recognizers must be a list")

        parsed_recognizers = []
        for recognizer in v:
            if isinstance(recognizer, str):
                # Simple string recognizer name - treat as predefined
                parsed_recognizers.append(recognizer)
                continue

            if isinstance(recognizer, dict):
                recognizer_type = recognizer.get("type")

                # Validate conflicting custom-only fields if explicitly predefined
                if recognizer_type == "predefined" and (
                    "patterns" in recognizer or "deny_list" in recognizer
                ):
                    raise ValueError(
                        f"Recognizer '{recognizer.get('name')}' is marked "
                        f"as 'predefined' but contains 'patterns' or 'deny_list' "
                        f"which are only valid for custom recognizers. "
                        f"Either use type: 'custom' or remove these fields."
                    )

                # Auto-detect type if not provided
                if not recognizer_type:
                    if "patterns" in recognizer or "deny_list" in recognizer:
                        recognizer_type = "custom"
                        recognizer_name = recognizer.get("name")
                        if recognizer_name:
                            cls.__check_if_predefined(recognizer_name)
                    else:
                        recognizer_type = "predefined"
                    recognizer["type"] = recognizer_type

                # Final append based on resolved type (only once)
                if recognizer_type == "predefined":
                    parsed_recognizers.append(PredefinedRecognizerConfig(**recognizer))
                elif recognizer_type == "custom":
                    parsed_recognizers.append(CustomRecognizerConfig(**recognizer))
                else:
                    raise ValueError(
                        f"Invalid recognizer type: {recognizer_type}. "
                        f"Must be 'predefined' or 'custom'."
                    )
                continue

            # Fallback: unrecognized structure, keep as-is
            parsed_recognizers.append(recognizer)

        return parsed_recognizers

    @classmethod
    def __check_if_predefined(cls, recognizer_name: Any | None):
        try:
            from presidio_analyzer.recognizer_registry.recognizers_loader_utils import (
                RecognizerListLoader,
            )

            try:
                RecognizerListLoader.get_existing_recognizer_cls(recognizer_name)
                raise ValueError(
                    f"Recognizer '{recognizer_name}' is a recognizer predefined in "
                    f"code but has 'patterns' or 'deny_list' defined. "
                    f"Either use type: 'predefined' "
                    f"or choose a different name for your custom recognizer."
                )
            except ValueError as e:
                if "was not found" not in str(e):
                    raise
        except ImportError:
            pass

    @model_validator(mode="after")
    def validate_language_presence(self):
        """Ensure custom recognizers define languages if no global languages are set."""
        if self.recognizers and (
            not self.supported_languages or len(self.supported_languages) == 0
        ):
            any_language_defined = False
            custom_without_language_present = False
            for r in self.recognizers:
                if isinstance(r, (PredefinedRecognizerConfig, CustomRecognizerConfig)):
                    # Track if any language is defined
                    if (r.supported_language and r.supported_language.strip()) or (
                        r.supported_languages and len(r.supported_languages) > 0
                    ):
                        any_language_defined = True
                    # Track custom recognizers lacking language info
                    if (
                        isinstance(r, CustomRecognizerConfig)
                        and not r.supported_language
                        and not r.supported_languages
                    ):
                        custom_without_language_present = True

            if custom_without_language_present and not any_language_defined:
                raise ValueError(
                    "Language configuration missing for custom recognizer(s): "
                    "provide 'supported_languages' at registry level "
                    "or specify languages for each custom recognizer."
                )
        return self
