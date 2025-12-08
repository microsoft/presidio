import pytest

from presidio_analyzer.input_validation import validate_language_codes


def test_configuration_validator_language_codes_no_exception():
    """Test ConfigurationValidator accepts valid language codes."""
    valid_languages = ["en", "es", "fr", "en-US", "es-ES"]
    validate_language_codes(valid_languages)

def test_configuration_validator_language_codes_invalid():
    """Test ConfigurationValidator rejects invalid language codes."""
    invalid_languages = ["invalid_lang"]

    with pytest.raises(ValueError) as exc_info:
        validate_language_codes(invalid_languages)

    assert "Invalid language code format" in str(exc_info.value)
