import re
from pathlib import Path
from typing import Any, Dict, List, Union

from pydantic import ValidationError

from .yaml_recognizer_models import RecognizerRegistryConfig


class ConfigurationValidator:
    """Class for validating configurations using Pydantic-enabled classes."""

    @staticmethod
    def validate_language_codes(languages: List[str]) -> List[str]:
        """Validate language codes format.

        :param languages: List of languages to validate.
        """
        for lang in languages:
            if not re.match(r"^[a-z]{2}(-[A-Z]{2})?$", lang):
                raise ValueError(
                    f"Invalid language code format: {lang}. "
                    f"Expected format: 'en' or 'en-US'"
                )
        return languages

    @staticmethod
    def validate_file_path(file_path: Union[str, Path]) -> Path:
        """Validate file path exists and is readable.

        :param file_path: Path to validate.
        """
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"Configuration file does not exist: {path}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        return path

    @staticmethod
    def validate_score_threshold(threshold: float) -> float:
        """Validate score threshold is within valid range.

        :param threshold: score threshold to validate.
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(
                f"Score threshold must be between 0.0 and 1.0, got: {threshold}"
            )
        return threshold

    @staticmethod
    def validate_nlp_configuration(config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate NLP validation structure.

        :param config: NLP Configuration to validate.
        """
        if not isinstance(config, dict):
            raise ValueError("NLP validation must be a dictionary")

        required_fields = ["nlp_engine_name", "models"]
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            raise ValueError(
                f"NLP validation missing required fields: {missing_fields}"
            )

        # Validate models structure
        if not isinstance(config["models"], list) or not config["models"]:
            raise ValueError("Models must be a non-empty list")

        for model in config["models"]:
            if not isinstance(model, dict):
                raise ValueError("Each model must be a dictionary")
            if "lang_code" not in model or "model_name" not in model:
                raise ValueError("Each model must have 'lang_code' and 'model_name'")

        return config

    @staticmethod
    def validate_recognizer_registry_configuration(
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Validate recognizer registry validation using Pydantic models."""
        try:
            # Use Pydantic model for validation
            validated_config = RecognizerRegistryConfig(**config)
            # Use model_dump() without exclude_unset to include default values
            return validated_config.model_dump(exclude_unset=False)
        except ValidationError as e:
            # Format the error in a human-readable way
            formatted_error = ConfigurationValidator._format_custom_recognziers_errors(
                e
            )
            raise ValueError(formatted_error)
        except ImportError:
            # Fallback to basic validation if models not available
            return ConfigurationValidator._validate_recognizer_registry_basic(config)

    @staticmethod
    def _validate_recognizer_registry_basic(config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate recognizer registry config."""
        if not isinstance(config, dict):
            raise ValueError("Recognizer registry validation must be a dictionary")

        # Define valid top-level keys for recognizer registry configuration
        valid_keys = {"supported_languages", "global_regex_flags", "recognizers"}

        # Check for unknown keys
        unknown_keys = set(config.keys()) - valid_keys
        if unknown_keys:
            raise ValueError(
                f"Unknown configuration key(s) in "
                f"recognizer_registry: {sorted(unknown_keys)}. "
                f"Valid keys are: {sorted(valid_keys)}"
            )

        # Validate supported languages
        if "supported_languages" in config:
            ConfigurationValidator.validate_language_codes(
                config["supported_languages"]
            )

        # Validate recognizers list
        if "recognizers" in config and not isinstance(config["recognizers"], list):
            raise ValueError("Recognizers must be a list")

        return config

    @staticmethod
    def validate_analyzer_configuration(config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate analyzer engine validation."""
        if not isinstance(config, dict):
            raise ValueError("Analyzer validation must be a dictionary")

        # Define valid top-level keys for analyzer configuration
        valid_keys = {
            "supported_languages",
            "default_score_threshold",
            "nlp_configuration",
            "recognizer_registry",
        }

        # Check for unknown keys
        unknown_keys = set(config.keys()) - valid_keys
        if unknown_keys:
            raise ValueError(
                f"Unknown configuration key(s) in analyzer "
                f"configuration: {sorted(unknown_keys)}. "
                f"Valid keys are: {sorted(valid_keys)}"
            )

        # Validate supported languages if present
        if "supported_languages" in config:
            ConfigurationValidator.validate_language_codes(
                config["supported_languages"]
            )

        # Validate score threshold if present
        if "default_score_threshold" in config:
            ConfigurationValidator.validate_score_threshold(
                config["default_score_threshold"]
            )

        # Validate nested configurations
        if "nlp_configuration" in config:
            ConfigurationValidator.validate_nlp_configuration(
                config["nlp_configuration"]
            )

        if "recognizer_registry" in config:
            if not isinstance(config["recognizer_registry"], dict):
                raise ValueError("recognizer_registry must be a dictionary")

        return config

    @staticmethod
    def _format_custom_recognziers_errors(error: ValidationError) -> str:
        """Format Pydantic ValidationError into human-readable message.

        :param error: Pydantic ValidationError to format
        :return: Human-readable error message
        """
        messages = []
        messages.append("Configuration validation failed:\n")

        for err in error.errors():
            error_type = err.get("type", "")
            location = " -> ".join(str(loc) for loc in err.get("loc", []))
            msg = err.get("msg", "")
            input_value = err.get("input", None)

            # Build a more readable error message based on error type and location
            if error_type == "missing":
                # Handle missing required fields
                field_name = err["loc"][-1] if err.get("loc") else "field"

                if "recognizers" in location and field_name == "supported_entity":
                    messages.append(
                        f"  ✗ Missing required field '{field_name}' "
                        f"in custom recognizer\n"
                        f"    Location: {location}\n"
                        f"    Fix: Add 'supported_entity' to specify which "
                        f"entity type this recognizer detects.\n"
                        f"    Example:\n"
                        f'      supported_entity: "MY_ENTITY"\n'
                    )
                elif field_name == "patterns":
                    messages.append(
                        f"  ✗ Custom recognizer is missing 'patterns' or 'deny_list'\n"
                        f"    Location: {location}\n"
                        f"    Fix: Add at least one of the following:\n"
                        f"      - patterns: List of regex patterns to match\n"
                        f"      - deny_list: List of words to detect\n"
                        f"    Example:\n"
                        f'      context: ["my", "entity", "keyword"]\n'
                        f"      patterns:\n"
                        f'        - name: "my_pattern"\n'
                        f'          regex: "[A-Z]{{3}}-\\d{{4}}"\n'
                        f"          score: 0.8\n"
                    )
                else:
                    messages.append(
                        f"  ✗ Missing required field: '{field_name}'\n"
                        f"    Location: {location}\n"
                        f"    Fix: This field is required. "
                        f"Please add it to your configuration.\n"
                    )

            elif error_type == "value_error":
                # Handle custom validation errors
                # Check if it's the missing patterns/deny_list error
                if "patterns" in msg.lower() and "deny_list" in msg.lower():
                    messages.append(
                        f"  ✗ Custom recognizer is missing 'patterns' or 'deny_list'\n"
                        f"    Location: {location}\n"
                        f"    Error: {msg}\n"
                        f"    Fix: Add at least one of the following:\n"
                        f"      - patterns: List of regex patterns to match\n"
                        f"      - deny_list: List of words to detect\n"
                        f"    Example:\n"
                        f'      context: ["my", "entity", "keyword"]\n'
                        f"      patterns:\n"
                        f'        - name: "my_pattern"\n'
                        f'          regex: "[A-Z]{{3}}-\\d{{4}}"\n'
                        f"          score: 0.8\n"
                    )
                else:
                    messages.append(
                        f"  ✗ Validation error at: {location}\n" f"    Error: {msg}\n"
                    )

            elif error_type in ("string_type", "list_type", "dict_type"):
                # Handle type errors
                expected_type = error_type.replace("_type", "")
                messages.append(
                    f"  ✗ Type error at: {location}\n"
                    f"    Expected: {expected_type}\n"
                    f"    Got: {type(input_value).__name__ if input_value is not None else 'None'}\n" # noqa: E501
                    f"    Value: {input_value}\n"
                )

            elif "union" in error_type:
                # Handle union type errors
                messages.append(
                    f"  ✗ Invalid value at: {location}\n" f"    Error: {msg}\n"
                )

            else:
                # Generic error message
                messages.append(f"  ✗ Error at: {location}\n" f"    {msg}\n")

        # Add helpful tips at the end
        messages.append("\n💡 Common fixes for custom recognizers:")
        messages.append("  • Ensure 'type: custom' is set")
        messages.append("  • Add 'supported_entity' (e.g., 'MY_ENTITY')")
        messages.append("  • Define 'patterns' or 'deny_list'")
        messages.append(
            "  • Specify language(s) via 'supported_language' or 'supported_languages'"
        )
        messages.append(
            "  • Optionally add 'context' words to improve detection accuracy"
        )
        messages.append("\n  Example custom recognizer:")
        messages.append("    recognizers:")
        messages.append('      - name: "MyRecognizer"')
        messages.append('        type: "custom"')
        messages.append('        supported_entity: "MY_ENTITY"')
        messages.append('        supported_language: "en"')
        messages.append('        context: ["my", "entity", "keyword"]')
        messages.append("        patterns:")
        messages.append('          - name: "my_pattern"')
        messages.append('            regex: "[A-Z]{3}-\\d{4}"')
        messages.append("            score: 0.8")

        return "\n".join(messages)
