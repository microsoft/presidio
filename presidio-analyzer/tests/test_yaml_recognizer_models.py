"""Tests for YAML recognizer configuration models."""

import pytest
from pydantic import ValidationError

from presidio_analyzer.input_validation.yaml_recognizer_models import (
    BaseRecognizerConfig,
    CustomRecognizerConfig,
    LanguageContextConfig,
    PredefinedRecognizerConfig,
    RecognizerRegistryConfig,
    YamlRecognizerProcessor,
)


def test_language_context_config_valid():
    """Test LanguageContextConfig validates correctly."""
    lang_config = LanguageContextConfig(
        language="en",
        context=["credit", "card"]
    )
    assert lang_config.language == "en"
    assert lang_config.context == ["credit", "card"]


def test_language_context_config_valid_with_region():
    """Test LanguageContextConfig with region code."""
    lang_config = LanguageContextConfig(
        language="en-US",
        context=["social", "security"]
    )
    assert lang_config.language == "en-US"
    assert lang_config.context == ["social", "security"]


def test_language_context_config_no_context():
    """Test LanguageContextConfig without context."""
    lang_config = LanguageContextConfig(language="es")
    assert lang_config.language == "es"
    assert lang_config.context is None


def test_language_context_config_invalid_language():
    """Test LanguageContextConfig rejects invalid language codes."""
    with pytest.raises(ValidationError) as exc_info:
        LanguageContextConfig(language="invalid")
    assert "Invalid language code format" in str(exc_info.value)


def test_language_context_config_invalid_format():
    """Test various invalid language formats."""
    invalid_languages = ["e", "eng", "EN", "en-us", "en-USA", "123", ""]

    for lang in invalid_languages:
        with pytest.raises(ValidationError):
            LanguageContextConfig(language=lang)


def test_base_recognizer_config_minimal():
    """Test minimal valid configuration."""
    config = BaseRecognizerConfig(name="test_recognizer")
    assert config.name == "test_recognizer"
    assert config.enabled is True
    assert config.type == "predefined"


def test_base_recognizer_config_full():
    """Test full configuration with all fields."""
    config = BaseRecognizerConfig(
        name="test_recognizer",
        enabled=False,
        type="custom",
        supported_language="en",
        context=["test", "context"],
        supported_entity="TEST_ENTITY"
    )
    assert config.name == "test_recognizer"
    assert config.enabled is False
    assert config.type == "custom"
    assert config.supported_languages == ["en"]
    assert config.supported_language is None  # Should be normalized
    assert config.context == ["test", "context"]
    assert config.supported_entities == ["TEST_ENTITY"]
    assert config.supported_entity is None  # Should be normalized


def test_language_normalization_single_to_multiple():
    """Test that supported_language gets normalized to supported_languages."""
    config = BaseRecognizerConfig(
        name="test",
        supported_language="en"
    )
    assert config.supported_languages == ["en"]
    assert config.supported_language is None


def test_entity_normalization_single_to_multiple():
    """Test that supported_entity gets normalized to supported_entities."""
    config = BaseRecognizerConfig(
        name="test",
        supported_entity="PERSON"
    )
    assert config.supported_entities == ["PERSON"]
    assert config.supported_entity is None


def test_cannot_specify_both_language_formats():
    """Test that specifying both language formats raises error."""
    with pytest.raises(ValidationError) as exc_info:
        BaseRecognizerConfig(
            name="test",
            supported_language="en",
            supported_languages=["es", "fr"]
        )
    assert "Cannot specify both 'supported_language' and 'supported_languages'" in str(exc_info.value)


def test_cannot_specify_both_entity_formats():
    """Test that specifying both entity formats raises error."""
    with pytest.raises(ValidationError) as exc_info:
        BaseRecognizerConfig(
            name="test",
            supported_entity="PERSON",
            supported_entities=["LOCATION", "ORG"]
        )
    assert "Cannot specify both 'supported_entity' and 'supported_entities'" in str(exc_info.value)


def test_invalid_single_language_format():
    """Test validation of single language format."""
    with pytest.raises(ValidationError):
        BaseRecognizerConfig(
            name="test",
            supported_language="invalid"
        )


def test_context_with_multiple_languages_error():
    """Test that global context with multiple languages raises error."""
    with pytest.raises(ValidationError) as exc_info:
        BaseRecognizerConfig(
            name="test",
            supported_languages=["en", "es"],
            context=["global", "context"]
        )
    assert "Global context can only be used with a single language" in str(exc_info.value)


def test_context_with_single_language_valid():
    """Test that global context with single language is valid."""
    config = BaseRecognizerConfig(
        name="test",
        supported_languages=["en"],
        context=["global", "context"]
    )
    assert config.context == ["global", "context"]


def test_predefined_recognizer_config_defaults():
    """Test predefined recognizer with defaults."""
    config = PredefinedRecognizerConfig(name="CreditCardRecognizer")
    assert config.name == "CreditCardRecognizer"
    assert config.type == "predefined"
    assert config.enabled is True


def test_predefined_recognizer_config_with_language():
    """Test predefined recognizer with language specification."""
    config = PredefinedRecognizerConfig(
        name="CreditCardRecognizer",
        supported_language="en"
    )
    assert config.supported_languages == ["en"]


def test_custom_recognizer_config_with_patterns():
    """Test custom recognizer with patterns."""
    patterns = [
        {
            "name": "test_pattern",
            "regex": r"\b\d{4}-\d{4}-\d{4}-\d{4}\b",
            "score": 0.8
        }
    ]
    config = CustomRecognizerConfig(
        name="custom_test",
        supported_entity="CUSTOM_ENTITY",
        patterns=patterns
    )
    assert config.name == "custom_test"
    assert config.type == "custom"
    assert config.supported_entities == ["CUSTOM_ENTITY"]
    assert config.patterns == patterns


def test_custom_recognizer_config_with_deny_list():
    """Test custom recognizer with deny list only."""
    config = CustomRecognizerConfig(
        name="custom_test",
        supported_entity="CUSTOM_ENTITY",
        deny_list=["exclude", "this"],
        deny_list_score=0.1
    )
    assert config.deny_list == ["exclude", "this"]
    assert config.deny_list_score == 0.1


def test_custom_recognizer_config_invalid_patterns_not_list():
    """Test that patterns must be a list."""
    with pytest.raises(ValidationError) as exc_info:
        CustomRecognizerConfig(
            name="test",
            supported_entity="TEST",
            patterns="not a list"
        )


def test_custom_recognizer_config_invalid_pattern_not_dict():
    """Test that each pattern must be a dict."""
    with pytest.raises(ValidationError) as exc_info:
        CustomRecognizerConfig(
            name="test",
            supported_entity="TEST",
            patterns=["not a dict"]
        )


def test_custom_recognizer_config_pattern_missing_fields():
    """Test that patterns must have required fields."""
    required_fields = ["name", "regex", "score"]

    for field in required_fields:
        pattern = {"name": "test", "regex": r"\d+", "score": 0.5}
        del pattern[field]

        with pytest.raises(ValidationError) as exc_info:
            CustomRecognizerConfig(
                name="test",
                supported_entity="TEST",
                patterns=[pattern]
            )


def test_custom_recognizer_config_invalid_score_type():
    """Test that pattern score must be float."""
    pattern = {
        "name": "test",
        "regex": r"\d+",
        "score": "not a float"
    }
    with pytest.raises(ValidationError) as exc_info:
        CustomRecognizerConfig(
            name="test",
            supported_entity="TEST",
            patterns=[pattern]
        )


def test_custom_recognizer_config_invalid_score_range():
    """Test that pattern score must be between 0 and 1."""
    invalid_scores = [-0.1, 1.1, 2.0]

    for score in invalid_scores:
        pattern = {
            "name": "test",
            "regex": r"\d+",
            "score": score
        }
        with pytest.raises(ValidationError) as exc_info:
            CustomRecognizerConfig(
                name="test",
                supported_entity="TEST",
                patterns=[pattern]
            )


def test_custom_recognizer_config_no_patterns_or_deny_list():
    """Test that custom recognizer must have patterns or deny_list."""
    with pytest.raises(ValidationError) as exc_info:
        CustomRecognizerConfig(
            name="test",
            supported_entity="TEST"
        )


def test_custom_recognizer_config_invalid_deny_list_score():
    """Test deny_list_score validation."""
    with pytest.raises(ValidationError):
        CustomRecognizerConfig(
            name="test",
            supported_entity="TEST",
            deny_list=["test"],
            deny_list_score=1.5  # Invalid: > 1.0
        )

    with pytest.raises(ValidationError):
        CustomRecognizerConfig(
            name="test",
            supported_entity="TEST",
            deny_list=["test"],
            deny_list_score=-0.1  # Invalid: < 0.0
        )


def test_recognizer_registry_config_defaults():
    """Test registry config with defaults."""
    config = RecognizerRegistryConfig()
    assert config.supported_languages is None
    assert config.global_regex_flags == 26
    assert config.recognizers == []


def test_recognizer_registry_config_valid_languages():
    """Test registry with valid languages."""
    config = RecognizerRegistryConfig(
        supported_languages=["en", "es", "fr-CA"]
    )
    assert config.supported_languages == ["en", "es", "fr-CA"]


def test_recognizer_registry_config_invalid_language():
    """Test registry with invalid language codes."""
    with pytest.raises(ValidationError):
        RecognizerRegistryConfig(
            supported_languages=["en", "invalid", "es"]
        )


def test_recognizer_registry_config_empty_languages():
    """Test registry with empty languages list."""
    config = RecognizerRegistryConfig(supported_languages=[])
    assert config.supported_languages == []


def test_recognizer_registry_config_string_recognizers():
    """Test registry with string recognizers."""
    config = RecognizerRegistryConfig(
        recognizers=["credit_card", "email", "phone_number"]
    )
    assert len(config.recognizers) == 3
    assert all(isinstance(r, str) for r in config.recognizers)


def test_recognizer_registry_config_mixed_recognizers():
    """Test registry with mixed recognizer types and missing languages should fail."""
    custom_config = {
        "name": "custom_test",
        "type": "custom",
        "supported_entity": "TEST",
        "patterns": [{"name": "test", "regex": r"\d+", "score": 0.5}]
    }

    with pytest.raises(ValidationError) as exc_info:
        RecognizerRegistryConfig(
            recognizers=[
                "credit_card",  # string predefined
                {"name": "UrlRecognizer", "type": "predefined"},  # predefined
                custom_config  # custom without languages should trigger error
            ]
        )
    assert "Language configuration missing" in str(exc_info.value)


def test_recognizer_registry_config_only_predefined_no_languages():
    """Predefined recognizers without languages should be allowed (use defaults)."""
    config = RecognizerRegistryConfig(
        recognizers=[
            "credit_card",
            {"name": "UrlRecognizer", "type": "predefined"},
        ]
    )
    assert len(config.recognizers) == 2
    assert isinstance(config.recognizers[0], str)
    assert isinstance(config.recognizers[1], PredefinedRecognizerConfig)


def test_recognizer_registry_config_auto_detect_type():
    """Test auto-detection of recognizer type based on patterns and deny_list."""
    # Should be detected as custom due to patterns
    custom_with_patterns_config = {
        "name": "auto_custom_patterns",
        "supported_entity": "TEST",
        "supported_language": "en",
        "patterns": [{"name": "test", "regex": r"\d+", "score": 0.5}]
    }

    # Should be detected as custom due to deny_list
    custom_with_deny_list_config = {
        "name": "auto_custom_deny",
        "supported_entity": "TEST",
        "supported_language": "en",
        "deny_list": ["exclude_this"]
    }

    # Should be detected as predefined (no patterns or deny_list)
    predefined_config = {
        "name": "UrlRecognizer",
        "enabled": True
    }

    config = RecognizerRegistryConfig(
        supported_languages=["en"],  # Add global language to satisfy new validation
        recognizers=[custom_with_patterns_config, custom_with_deny_list_config, predefined_config]
    )

    assert isinstance(config.recognizers[0], CustomRecognizerConfig)
    assert config.recognizers[0].type == "custom"
    assert isinstance(config.recognizers[1], CustomRecognizerConfig)
    assert config.recognizers[1].type == "custom"
    assert isinstance(config.recognizers[2], PredefinedRecognizerConfig)
    assert config.recognizers[2].type == "predefined"


def test_expand_predefined_recognizer_single_language():
    """Test expanding predefined recognizer with single language."""
    config = PredefinedRecognizerConfig(
        name="EmailRecognizer",
        supported_language="en"
    )

    result = YamlRecognizerProcessor.expand_recognizer_configs(
        config, ["en", "es"]
    )

    assert len(result) == 1
    assert result[0]["name"] == "EmailRecognizer"
    assert result[0]["supported_language"] == "en"


def test_expand_predefined_recognizer_multiple_languages():
    """Test expanding predefined recognizer with multiple languages."""
    config = PredefinedRecognizerConfig(
        name="PhoneRecognizer",
        supported_languages=["en", "es"]
    )

    result = YamlRecognizerProcessor.expand_recognizer_configs(
        config, ["en", "es", "fr"]
    )

    assert len(result) == 2
    assert result[0]["supported_language"] == "en"
    assert result[1]["supported_language"] == "es"


def test_expand_predefined_recognizer_no_language():
    """Test that predefined recognizer with no language creates single config."""
    config = PredefinedRecognizerConfig(
        name="ItFiscalCodeRecognizer"
    )

    result = YamlRecognizerProcessor.expand_recognizer_configs(
        config, ["en", "es", "it"]
    )

    # Should create only one config, not one per registry language
    assert len(result) == 1
    # Should not have supported_language set (let recognizer use its default)
    assert "supported_language" not in result[0]
    assert "supported_languages" not in result[0]
    assert result[0]["name"] == "ItFiscalCodeRecognizer"
    assert result[0]["type"] == "predefined"


def test_expand_custom_recognizer_no_language_error():
    """Test that custom recognizer without language raises error."""
    config = CustomRecognizerConfig(
        name="custom_test",
        supported_entity="TEST",
        patterns=[{"name": "test", "regex": r"\d+", "score": 0.5}]
    )

    with pytest.raises(ValueError) as exc_info:
        YamlRecognizerProcessor.expand_recognizer_configs(
            config, ["en", "es"]
        )
    assert "Custom recognizer 'custom_test' must specify supported languages" in str(exc_info.value)


def test_expand_custom_recognizer_with_language():
    """Test expanding custom recognizer with specified language."""
    config = CustomRecognizerConfig(
        name="custom_test",
        supported_entity="TEST",
        supported_language="en",
        patterns=[{"name": "test", "regex": r"\d+", "score": 0.5}]
    )

    result = YamlRecognizerProcessor.expand_recognizer_configs(
        config, ["en", "es"]
    )

    assert len(result) == 1
    assert result[0]["name"] == "custom_test"
    assert result[0]["supported_language"] == "en"


def test_expand_recognizer_with_global_context():
    """Test that global context is preserved during expansion."""
    config = PredefinedRecognizerConfig(
        name="EmailRecognizer",
        supported_languages=["en"],
        context=["global", "context"]
    )

    result = YamlRecognizerProcessor.expand_recognizer_configs(
        config, ["en", "es"]
    )

    assert len(result) == 1
    assert result[0]["context"] == ["global", "context"]


def test_create_pattern_recognizers_from_config():
    """Test creating PatternRecognizer configs from CustomRecognizerConfig."""
    patterns = [
        {"name": "test", "regex": r"\d+", "score": 0.5}
    ]
    config = CustomRecognizerConfig(
        name="custom_test",
        supported_entity="TEST",
        supported_language="en",
        patterns=patterns,
        deny_list=["exclude"],
        deny_list_score=0.1
    )

    result = YamlRecognizerProcessor.create_pattern_recognizers_from_config(
        config, ["en"]
    )

    assert len(result) == 1
    pattern_config = result[0]
    assert pattern_config["name"] == "custom_test"
    assert pattern_config["supported_entities"] == ["TEST"]
    assert "supported_entity" not in pattern_config
    assert pattern_config["patterns"] == patterns
    assert pattern_config["deny_list"] == ["exclude"]
    assert pattern_config["deny_list_score"] == 0.1


def test_expand_language_context_config():
    """Test expanding recognizer with LanguageContextConfig."""
    lang_config = LanguageContextConfig(
        language="es",
        context=["tarjeta", "credito"]
    )
    config = CustomRecognizerConfig(
        name="credit_card_es",
        supported_entity="CREDIT_CARD",
        supported_languages=[lang_config],
        patterns=[{"name": "test", "regex": r"\d+", "score": 0.5}]
    )

    result = YamlRecognizerProcessor.expand_recognizer_configs(
        config, ["en", "es"]
    )

    assert len(result) == 1
    assert result[0]["supported_language"] == lang_config
    # Global context should be preserved even with language-specific config
    assert result[0]["context"] is None  # No global context in this case


def test_complete_registry_scenario():
    """Test a complete registry configuration scenario."""
    registry_config = {
        "supported_languages": ["en", "es"],
        "recognizers": [
            "credit_card",  # String recognizer (kept as string)
            {
                "name": "EmailRecognizer",
                "type": "predefined",
                "enabled": True
            },
            {
                "name": "custom_pattern",
                "type": "custom",
                "supported_entity": "CUSTOM_ID",
                "supported_language": "en",
                "patterns": [
                    {
                        "name": "id_pattern",
                        "regex": r"ID-\d{6}",
                        "score": 0.9
                    }
                ]
            }
        ]
    }

    config = RecognizerRegistryConfig(**registry_config)
    assert len(config.recognizers) == 3
    assert isinstance(config.recognizers[0], str)
    assert isinstance(config.recognizers[1], PredefinedRecognizerConfig)
    assert isinstance(config.recognizers[2], CustomRecognizerConfig)


def test_language_context_integration():
    """Test integration with LanguageContextConfig."""
    lang_configs = [
        LanguageContextConfig(language="en", context=["credit", "card"]),
        LanguageContextConfig(language="es", context=["tarjeta", "credito"])
    ]

    config = PredefinedRecognizerConfig(
        name="CreditCardRecognizer",
        supported_languages=lang_configs
    )

    # Test expansion
    result = YamlRecognizerProcessor.expand_recognizer_configs(
        config, ["en", "es", "fr"]
    )

    assert len(result) == 2
    assert result[0]["supported_language"] == lang_configs[0]
    assert result[1]["supported_language"] == lang_configs[1]


def test_error_handling_cascade():
    """Test that validation errors are properly cascaded."""
    # This should fail at the CustomRecognizerConfig level
    with pytest.raises(ValidationError) as exc_info:
        RecognizerRegistryConfig(
            recognizers=[
                {
                    "name": "invalid_custom",
                    "type": "custom",
                    "supported_entity": "TEST",
                    "patterns": [
                        {
                            "name": "test",
                            "regex": r"\d+",
                            "score": 2.0  # Invalid score > 1.0
                        }
                    ]
                }
            ]
        )
    assert "Pattern score should be between 0 and 1" in str(exc_info.value)


def test_predefined_recognizer_config_valid_recognizer():
    """Test predefined recognizer with valid recognizer name."""
    # Test with a common recognizer that should exist
    config = PredefinedRecognizerConfig(name="CreditCardRecognizer")
    assert config.name == "CreditCardRecognizer"
    assert config.type == "predefined"


def test_predefined_recognizer_config_invalid_recognizer():
    """Test predefined recognizer with invalid recognizer name."""
    with pytest.raises(ValidationError) as exc_info:
        PredefinedRecognizerConfig(name="NonExistentRecognizer")

    error_message = str(exc_info.value)
    assert "Predefined recognizer 'NonExistentRecognizer' not found" in error_message
    assert "Available predefined recognizers:" in error_message


def test_predefined_recognizer_config_case_sensitive():
    """Test that recognizer names are case sensitive."""
    with pytest.raises(ValidationError) as exc_info:
        PredefinedRecognizerConfig(name="creditcardrecognizer")  # lowercase

    error_message = str(exc_info.value)
    assert "Predefined recognizer 'creditcardrecognizer' not found" in error_message


def test_predefined_recognizer_validation_with_import_error():
    """Test that validation gracefully handles import errors."""
    import sys
    from unittest.mock import patch

    with patch.dict('sys.modules', {'presidio_analyzer.recognizer_registry.recognizers_loader_utils': None}):
        config = PredefinedRecognizerConfig(name="SomeRecognizer")
        assert config.name == "SomeRecognizer"
        assert config.type == "predefined"


def test_custom_recognizer_config_predefined_name_error():
    """Test that using a predefined recognizer name for custom recognizer raises error."""
    with pytest.raises(ValidationError) as exc_info:
        CustomRecognizerConfig(
            name="CreditCardRecognizer",  # This is a predefined recognizer
            type="custom",
            supported_entity="CREDIT_CARD",
            patterns=[{"name": "test", "regex": r"\d+", "score": 0.5}]
        )

    error_message = str(exc_info.value)
    assert "is a predefined recognizer but is marked as 'custom'" in error_message
    assert "Either use type: 'predefined' or choose a different name" in error_message


def test_custom_recognizer_config_unique_name_valid():
    """Test that custom recognizers with unique names are valid."""
    config = CustomRecognizerConfig(
        name="MyCustomRecognizer",  # This should not exist as predefined
        type="custom",
        supported_entity="CUSTOM_ENTITY",
        patterns=[{"name": "test", "regex": r"\d+", "score": 0.5}]
    )
    assert config.name == "MyCustomRecognizer"
    assert config.type == "custom"


def test_custom_recognizer_config_predefined_name_validation_with_import_error():
    """Test that validation gracefully handles import errors for predefined name checking."""
    from unittest.mock import patch

    # Mock the import to raise ImportError
    with patch.dict('sys.modules', {'presidio_analyzer.recognizer_registry.recognizers_loader_utils': None}):
        # This should not raise an error even if the import fails
        config = CustomRecognizerConfig(
            name="SomeRecognizer",
            type="custom",
            supported_entity="TEST",
            patterns=[{"name": "test", "regex": r"\d+", "score": 0.5}]
        )
        assert config.name == "SomeRecognizer"
        assert config.type == "custom"


def test_custom_recognizer_with_language_no_global_languages():
    """Custom recognizer specifying its own language should pass without global languages."""
    registry_config = {
        "recognizers": [
            {
                "name": "my_custom_with_lang",
                "type": "custom",
                "supported_entity": "TEST",
                "supported_language": "en",
                "patterns": [
                    {"name": "p", "regex": r"\d+", "score": 0.5}
                ]
            }
        ]
    }
    config = RecognizerRegistryConfig(**registry_config)
    assert len(config.recognizers) == 1
    assert isinstance(config.recognizers[0], CustomRecognizerConfig)
    assert config.recognizers[0].supported_languages == ["en"]
