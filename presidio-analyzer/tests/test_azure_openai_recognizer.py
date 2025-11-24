"""Tests for Azure OpenAI LangExtract recognizer using mocks.

Tests the hierarchy: LMRecognizer -> LangExtractRecognizer -> AzureOpenAILangExtractRecognizer

These tests use mocks to avoid requiring Azure OpenAI or actual LLM calls.
"""
import pytest
from unittest.mock import patch


class TestAzureOpenAILangExtractRecognizerInitialization:
    """Test AzureOpenAILangExtractRecognizer initialization and configuration loading."""

    def test_import_error_when_langextract_not_installed(self):
        """Test that ImportError is raised when langextract is not installed."""
        with patch(
            'presidio_analyzer.predefined_recognizers.third_party.'
            'azure_openai_langextract_recognizer.LANGEXTRACT_AVAILABLE',
            False
        ), patch.dict('os.environ', {'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/'}):
            from presidio_analyzer.predefined_recognizers.third_party.azure_openai_langextract_recognizer import AzureOpenAILangExtractRecognizer
            with pytest.raises(ImportError, match="LangExtract is not installed"):
                AzureOpenAILangExtractRecognizer()

    def test_missing_endpoint_raises_error(self, tmp_path):
        """Test that initialization fails when Azure endpoint is missing."""
        import yaml
        import os
        
        config = {
            "lm_recognizer": {
                "type": "AzureOpenAILangExtractRecognizer"
            },
            "langextract": {
                "supported_entities": ["PERSON"],
                "entity_mappings": {"person_name": "PERSON"},
                "prompt_file": "langextract_prompts/default_pii_phi_prompt.j2",
                "examples_file": "langextract_prompts/default_pii_phi_examples.yaml",
                "min_score": 0.5,
                "model": {
                    "model_id": "gpt-4",
                    "temperature": 0.0,
                }
            },
            "azure_openai": {
                "api_key": "test-key",
                "api_version": "2024-02-01",
            }
        }

        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        # Clear any environment variables that might provide endpoint
        env_without_azure = {k: v for k, v in os.environ.items() 
                            if not k.startswith('AZURE_OPENAI')}
        
        with patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'azure_openai_langextract_recognizer.LANGEXTRACT_AVAILABLE', True), \
             patch.dict('os.environ', env_without_azure, clear=True):
            
            from presidio_analyzer.predefined_recognizers.third_party.azure_openai_langextract_recognizer import AzureOpenAILangExtractRecognizer
            
            with pytest.raises(ValueError, match="azure_endpoint"):
                AzureOpenAILangExtractRecognizer(config_path=str(config_file))


class TestAzureOpenAIProvider:
    """Test the Azure OpenAI provider registration."""

    def test_provider_registration(self):
        """Test that Azure OpenAI provider is properly registered."""
        from presidio_analyzer.predefined_recognizers.third_party import azure_openai_provider
        assert hasattr(azure_openai_provider, 'AzureOpenAILanguageModel')

    def test_provider_import_error_when_dependencies_missing(self):
        """Test that provider handles missing dependencies gracefully."""
        from presidio_analyzer.predefined_recognizers.third_party import azure_openai_provider
        assert azure_openai_provider is not None

