"""Tests for LangExtract recognizer with real Ollama integration.

These tests require Ollama to be running and will auto-install it if needed.
Tests are skipped if Ollama setup fails.
"""
import pytest
from presidio_analyzer.predefined_recognizers import LangExtractRecognizer

# All tests require langextract and ollama to be available
pytestmark = pytest.mark.skip_engine("langextract")


class TestLangExtractRecognizerInitialization:
    """Test recognizer initialization and configuration loading."""

    def test_import_error_when_langextract_not_installed(self):
        """Test that ImportError is raised when langextract is not installed."""
        from unittest.mock import patch

        with patch(
            'presidio_analyzer.predefined_recognizers.third_party.'
            'langextract_recognizer.LANGEXTRACT_AVAILABLE',
            False
        ):
            with pytest.raises(ImportError, match="LangExtract is not installed"):
                LangExtractRecognizer()

    def test_initialization_with_real_ollama(self, langextract_recognizer_class):
        """Test recognizer initialization with real Ollama.

        This test verifies:
        - Config loading works
        - Ollama server is reachable
        - Model is available (or auto-downloaded)
        - Recognizer initializes successfully
        """
        if not langextract_recognizer_class:
            pytest.skip("LangExtract not available")

        recognizer = langextract_recognizer_class()

        assert recognizer.enabled is True
        assert recognizer.model_id is not None
        assert recognizer.model_url is not None
        assert len(recognizer.supported_entities) > 0

    def test_disabled_recognizer_still_initializes(
        self, langextract_recognizer_class, tmp_path
    ):
        """Test that disabled recognizer initializes without validation."""
        if not langextract_recognizer_class:
            pytest.skip("LangExtract not available")


        import yaml

        # Create config with enabled=False
        config = {
            "langextract": {
                "enabled": False,
                "model_id": "gemma2:2b",
                "model_url": "http://localhost:11434",
                "temperature": 0.0,
                "min_score": 0.5,
                "supported_entities": ["PERSON"],
                "entity_mappings": {"person": "PERSON"},
                "prompt_file": "langextract_prompts/default_pii_prompt.txt",
                "examples_file": "langextract_prompts/default_pii_examples.yaml",
            }
        }

        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        recognizer = langextract_recognizer_class(config_path=str(config_file))

        assert recognizer.enabled is False

    def test_missing_required_config_raises_error(
        self, langextract_recognizer_class, tmp_path
    ):
        """Test that missing required config field raises ValueError."""
        if not langextract_recognizer_class:
            pytest.skip("LangExtract not available")

        import yaml

        # Missing 'model_url' - required field
        config = {
            "langextract": {
                "enabled": False,
                "model_id": "gemma2:2b",
                "temperature": 0.0,
                "min_score": 0.5,
                "supported_entities": ["PERSON"],
                "entity_mappings": {"person": "PERSON"},
                "prompt_file": "langextract_prompts/default_pii_prompt.txt",
                "examples_file": "langextract_prompts/default_pii_examples.yaml",
            }
        }

        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        with pytest.raises(ValueError, match="Missing required configuration"):
            langextract_recognizer_class(config_path=str(config_file))


class TestLangExtractRecognizerOllamaValidation:
    """Test Ollama server and model validation with real connection."""

    def test_recognizer_validates_ollama_on_init(
        self, langextract_recognizer_class
    ):
        """Test that recognizer validates Ollama during initialization.

        This is an integration test that verifies:
        - Ollama server is checked
        - Model availability is verified
        - Auto-download happens if needed
        """
        if not langextract_recognizer_class:
            pytest.skip("LangExtract not available")

        # This should succeed because conftest.py ensures Ollama is ready
        recognizer = langextract_recognizer_class()

        # If we get here, validation passed
        assert recognizer.model_id is not None


class TestLangExtractRecognizerAnalyze:
    """Test the analyze method with real Ollama."""

    def test_analyze_disabled_recognizer_returns_empty(
        self, langextract_recognizer_class, tmp_path
    ):
        """Test that disabled recognizer returns empty results."""
        if not langextract_recognizer_class:
            pytest.skip("LangExtract not available")

        import yaml

        config = {
            "langextract": {
                "enabled": False,
                "model_id": "gemma2:2b",
                "model_url": "http://localhost:11434",
                "temperature": 0.0,
                "min_score": 0.5,
                "supported_entities": [],
                "entity_mappings": {},
                "prompt_file": "langextract_prompts/default_pii_prompt.txt",
                "examples_file": "langextract_prompts/default_pii_examples.yaml",
            }
        }

        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        recognizer = langextract_recognizer_class(config_path=str(config_file))
        results = recognizer.analyze("Test text")

        assert results == []

    def test_analyze_empty_text_returns_empty(self, langextract_recognizer_class):
        """Test that empty text returns empty results."""
        if not langextract_recognizer_class:
            pytest.skip("LangExtract not available")

        recognizer = langextract_recognizer_class()
        results = recognizer.analyze("")

        assert results == []

    def test_analyze_with_person_entity(self, langextract_recognizer_class):
        """Test analysis detecting a person entity with real Ollama."""
        if not langextract_recognizer_class:
            pytest.skip("LangExtract not available")

        recognizer = langextract_recognizer_class()
        text = "My name is John Doe"
        results = recognizer.analyze(text, entities=["PERSON"])

        # Should detect at least the person
        assert len(results) > 0

        # Find the PERSON entity
        person_results = [r for r in results if r.entity_type == "PERSON"]
        assert len(person_results) > 0

        # Verify the entity has valid properties
        person_result = person_results[0]
        assert person_result.start >= 0
        assert person_result.end <= len(text)
        assert person_result.start < person_result.end
        assert 0.0 <= person_result.score <= 1.0

    def test_analyze_with_email_entity(self, langextract_recognizer_class):
        """Test analysis detecting an email entity with real Ollama."""
        if not langextract_recognizer_class:
            pytest.skip("LangExtract not available")

        recognizer = langextract_recognizer_class()
        text = "Contact me at john@example.com"
        results = recognizer.analyze(text, entities=["EMAIL_ADDRESS"])

        # Should detect the email
        assert len(results) > 0

        email_results = [r for r in results if r.entity_type == "EMAIL_ADDRESS"]
        assert len(email_results) > 0

        email_result = email_results[0]
        assert email_result.start >= 0
        assert email_result.end <= len(text)
        assert 0.0 <= email_result.score <= 1.0

    def test_analyze_with_phone_entity(self, langextract_recognizer_class):
        """Test analysis detecting a phone number with real Ollama."""
        if not langextract_recognizer_class:
            pytest.skip("LangExtract not available")

        recognizer = langextract_recognizer_class()
        text = "Call me at 555-123-4567"
        results = recognizer.analyze(text, entities=["PHONE_NUMBER"])

        # Should detect the phone number
        assert len(results) > 0

        phone_results = [r for r in results if r.entity_type == "PHONE_NUMBER"]
        assert len(phone_results) > 0

        phone_result = phone_results[0]
        assert phone_result.start >= 0
        assert phone_result.end <= len(text)
        assert 0.0 <= phone_result.score <= 1.0

    def test_analyze_with_multiple_entities(self, langextract_recognizer_class):
        """Test analysis detecting multiple entity types with real Ollama."""
        if not langextract_recognizer_class:
            pytest.skip("LangExtract not available")

        recognizer = langextract_recognizer_class()
        text = "John Doe's email is john@example.com and phone is 555-1234"
        results = recognizer.analyze(text)

        # Should detect multiple entities
        assert len(results) > 0

        # Check that we have at least some of the expected entity types
        detected_types = {r.entity_type for r in results}
        expected_types = {"PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"}

        # Should have at least one of the expected types
        assert len(detected_types.intersection(expected_types)) > 0

        # All results should have valid properties
        for result in results:
            assert result.start >= 0
            assert result.end <= len(text)
            assert result.start < result.end
            assert 0.0 <= result.score <= 1.0

    def test_analyze_filters_by_requested_entities(
        self, langextract_recognizer_class
    ):
        """Test that only requested entities are returned."""
        if not langextract_recognizer_class:
            pytest.skip("LangExtract not available")

        recognizer = langextract_recognizer_class()
        text = "John Doe's email is john@example.com"

        # Only request EMAIL_ADDRESS
        results = recognizer.analyze(text, entities=["EMAIL_ADDRESS"])

        # Should only return EMAIL_ADDRESS, not PERSON
        entity_types = {r.entity_type for r in results}
        assert "EMAIL_ADDRESS" in entity_types or len(results) == 0
        # PERSON should not be in results
        assert "PERSON" not in entity_types

    def test_analyze_returns_analysis_explanation(
        self, langextract_recognizer_class
    ):
        """Test that results include analysis explanation."""
        if not langextract_recognizer_class:
            pytest.skip("LangExtract not available")

        recognizer = langextract_recognizer_class()
        text = "My name is John Doe"
        results = recognizer.analyze(text, entities=["PERSON"])

        if len(results) > 0:
            result = results[0]
            assert result.analysis_explanation is not None
            assert result.analysis_explanation.recognizer == "LangExtractRecognizer"


class TestLangExtractRecognizerErrorHandling:
    """Test error handling with mocked error conditions."""

    def test_connection_error_when_ollama_unreachable(
        self, langextract_recognizer_class, tmp_path
    ):
        """Test that unreachable Ollama server raises ConnectionError."""
        if not langextract_recognizer_class:
            pytest.skip("LangExtract not available")

        import yaml

        # Point to non-existent Ollama server
        config = {
            "langextract": {
                "enabled": True,
                "model_id": "gemma2:2b",
                "model_url": "http://localhost:99999",  # Invalid port
                "temperature": 0.0,
                "min_score": 0.5,
                "supported_entities": ["PERSON"],
                "entity_mappings": {"person": "PERSON"},
                "prompt_file": "langextract_prompts/default_pii_prompt.txt",
                "examples_file": "langextract_prompts/default_pii_examples.yaml",
            }
        }

        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        with pytest.raises(ConnectionError, match="Ollama server not reachable"):
            langextract_recognizer_class(config_path=str(config_file))


# Integration tests
@pytest.mark.parametrize(
    "text, expected_entity_types",
    [
        # Test PERSON entity
        ("My name is John Doe", ["PERSON"]),
        # Test PHONE_NUMBER entity
        ("Call me at 555-123-4567", ["PHONE_NUMBER"]),
        # Test EMAIL_ADDRESS entity
        ("Email: alice@example.com", ["EMAIL_ADDRESS"]),
        # Test multiple entities
        (
            "John Doe's email is john@example.com and phone is 555-1234",
            ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"]
        ),
    ],
)
def test_langextract_integration(
    text,
    expected_entity_types,
    langextract_recognizer_class,
):
    """Integration tests with real Ollama model.

    These tests verify the complete end-to-end functionality:
    - Ollama is running
    - Model is available
    - LangExtract can detect entities
    - Results are properly formatted
    """
    if not langextract_recognizer_class:
        pytest.skip("LangExtract not available")

    recognizer = langextract_recognizer_class()
    results = recognizer.analyze(text, entities=expected_entity_types)

    # Should detect at least some entities
    assert len(results) > 0

    # Check that detected entities match expected types
    detected_types = {r.entity_type for r in results}
    assert detected_types.intersection(set(expected_entity_types))

    # Check score range
    for result in results:
        assert 0.0 <= result.score <= 1.0
        assert result.start >= 0
        assert result.end <= len(text)
        assert result.start < result.end
        assert result.entity_type in expected_entity_types
