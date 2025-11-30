"""Tests for the Pydantic-based validation system using existing adapted classes."""
import pytest

from presidio_analyzer.input_validation import ConfigurationValidator


def test_configuration_validator_nlp_config_valid():
    """Test ConfigurationValidator accepts valid NLP validation."""
    valid_config = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "en", "model_name": "en_core_web_lg"}
        ]
    }

    validated = ConfigurationValidator.validate_nlp_configuration(valid_config)
    assert validated == valid_config

def test_configuration_validator_nlp_config_missing_fields():
    """Test ConfigurationValidator rejects NLP config with missing required fields."""
    invalid_config = {
        "nlp_engine_name": "spacy"
        # Missing "models" field
    }

    with pytest.raises(ValueError) as exc_info:
        ConfigurationValidator.validate_nlp_configuration(invalid_config)

    assert "missing required fields" in str(exc_info.value)

def test_configuration_validator_analyzer_config_valid():
    """Test ConfigurationValidator accepts valid analyzer validation."""
    valid_config = {
        "supported_languages": ["en", "es"],
        "default_score_threshold": 0.5,
        "nlp_configuration": {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}]
        }
    }

    validated = ConfigurationValidator.validate_analyzer_configuration(valid_config)
    assert validated == valid_config

def test_configuration_validator_analyzer_config_invalid_threshold():
    """Test ConfigurationValidator rejects invalid score threshold."""
    invalid_config = {
        "supported_languages": ["en"],
        "default_score_threshold": 1.5  # Invalid: > 1.0
    }

    with pytest.raises(ValueError) as exc_info:
        ConfigurationValidator.validate_analyzer_configuration(invalid_config)

    assert "must be between 0.0 and 1.0" in str(exc_info.value)

def test_file_path_validation_success(tmp_path):
    """Test file path validation with existing file."""
    test_file = tmp_path / "test.yaml"
    test_file.write_text("test: content")

    validated_path = ConfigurationValidator.validate_file_path(str(test_file))
    assert validated_path == test_file

def test_file_path_validation_nonexistent():
    """Test file path validation with non-existent file."""
    with pytest.raises(ValueError) as exc_info:
        ConfigurationValidator.validate_file_path("/nonexistent/file.yaml")

    assert "does not exist" in str(exc_info.value)

def test_configuration_validator_analyzer_config_unknown_keys():
    """Test ConfigurationValidator rejects analyzer config with unknown keys."""
    invalid_config = {
        "supported_languages": ["en"],
        "default_score_threshold": 0.5,
        "unknown_key": "some_value",
        "another_typo": 123
    }

    with pytest.raises(ValueError) as exc_info:
        ConfigurationValidator.validate_analyzer_configuration(invalid_config)

def test_configuration_validator_recognizer_registry_unknown_keys():
    """Test ConfigurationValidator rejects recognizer registry config with unknown keys."""
    invalid_config = {
        "supported_languages": ["en"],
        "global_regex_flags": 26,
        "recognizers": [],
        "invalid_field": "value",
        "typo_key": 456
    }

    with pytest.raises(ValueError) as exc_info:
        ConfigurationValidator.validate_recognizer_registry_configuration(invalid_config)

