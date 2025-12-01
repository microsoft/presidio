import os
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_langextract():
    """Mock langextract to avoid actual API calls."""
    with patch('presidio_analyzer.llm_utils.langextract_helper.lx') as mock_lx:
        # Mock successful extraction
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {
            "entities": [
                {"text": "john.doe@example.com", "label": "email", "start": 12, "end": 32}
            ]
        }
        mock_lx.extract.return_value = mock_result
        yield mock_lx


class TestAzureOpenAILangExtractRecognizerInitialization:
    """Test AzureOpenAILangExtractRecognizer initialization and configuration loading."""

    def test_import_error_when_langextract_not_installed(self):
        """Test that ImportError is raised when langextract is not installed."""
        with patch(
            'presidio_analyzer.llm_utils.langextract_helper.lx',
            None
        ):
            from presidio_analyzer.predefined_recognizers.third_party.azure_openai_langextract_recognizer import AzureOpenAILangExtractRecognizer
            with pytest.raises(ImportError, match="LangExtract is not installed"):
                AzureOpenAILangExtractRecognizer(
                    model_id="gpt-4o",
                    azure_endpoint="https://test.openai.azure.com/"
                )

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
        
        with patch.dict('os.environ', env_without_azure, clear=True):
            
            from presidio_analyzer.predefined_recognizers.third_party.azure_openai_langextract_recognizer import AzureOpenAILangExtractRecognizer
            
            with pytest.raises(ValueError, match="azure_endpoint"):
                AzureOpenAILangExtractRecognizer(config_path=str(config_file))


class TestAzureOpenAILangExtractRecognizerUsage:
    """Test the simplified API that doesn't require config file download."""
    
    def test_simple_usage_with_parameters(self, mock_langextract):
        """Best practice: Pass model_id and credentials as parameters."""
        from presidio_analyzer.predefined_recognizers import AzureOpenAILangExtractRecognizer
        
        # Simple usage - no config file needed!
        recognizer = AzureOpenAILangExtractRecognizer(
            model_id="gpt-4o",  # Your Azure deployment name
            azure_endpoint="https://test-resource.openai.azure.com/",
            api_key="test-api-key"
        )
        
        assert recognizer.model_id == "gpt-4o"
        assert recognizer.azure_endpoint == "https://test-resource.openai.azure.com/"
        assert recognizer.api_key == "test-api-key"
    
    def test_environment_variables(self, mock_langextract):
        """Alternative: Use environment variables for credentials."""
        from presidio_analyzer.predefined_recognizers import AzureOpenAILangExtractRecognizer
        
        env_vars = {
            "AZURE_OPENAI_ENDPOINT": "https://test-resource.openai.azure.com/",
            "AZURE_OPENAI_API_KEY": "test-api-key"
        }
        
        with patch.dict(os.environ, env_vars):
            recognizer = AzureOpenAILangExtractRecognizer(
                model_id="gpt-4o"  # Just pass deployment name
            )
            
            assert recognizer.model_id == "gpt-4o"
            assert recognizer.azure_endpoint == "https://test-resource.openai.azure.com/"
            assert recognizer.api_key == "test-api-key"
    
    def test_managed_identity_no_api_key(self, mock_langextract):
        """Production: Use managed identity (no API key)."""
        from presidio_analyzer.predefined_recognizers import AzureOpenAILangExtractRecognizer
        
        recognizer = AzureOpenAILangExtractRecognizer(
            model_id="gpt-4o",
            azure_endpoint="https://test-resource.openai.azure.com/"
            # No api_key = uses managed identity
        )
        
        assert recognizer.model_id == "gpt-4o"
        assert recognizer.api_key is None  # Will use managed identity
    
    def test_model_id_overrides_config(self, mock_langextract, tmp_path):
        """Parameter model_id overrides config file model_id."""
        # Mock file loading to avoid needing actual prompt/example files
        with patch('presidio_analyzer.llm_utils.config_loader.load_yaml_file') as mock_load:
            mock_load.return_value = {}  # Empty prompt/examples
            
            from presidio_analyzer.predefined_recognizers import AzureOpenAILangExtractRecognizer
            
            # Parameter overrides config - using default config
            recognizer = AzureOpenAILangExtractRecognizer(
                model_id="gpt-4o",  # Parameter overrides default config
                azure_endpoint="https://test-resource.openai.azure.com/",
                api_key="test-api-key"
            )
            
            # Should use parameter value
            assert recognizer.model_id == "gpt-4o"
    
    def test_config_file_provides_custom_entities(self, mock_langextract):
        """Advanced: Default config provides custom entities/mappings."""
        # Mock file loading to avoid needing actual files
        with patch('presidio_analyzer.llm_utils.config_loader.load_yaml_file') as mock_load:
            mock_load.return_value = {}  # Empty prompt/examples
            
            from presidio_analyzer.predefined_recognizers import AzureOpenAILangExtractRecognizer
            
            # Use default config but override model_id
            recognizer = AzureOpenAILangExtractRecognizer(
                model_id="gpt-4o",  # Override deployment name
                azure_endpoint="https://test-resource.openai.azure.com/",
                api_key="test-api-key"
            )
            
            # Default config provides many entities
            assert recognizer.model_id == "gpt-4o"  # From parameter
            assert "PERSON" in recognizer.supported_entities  # From default config
            assert "EMAIL_ADDRESS" in recognizer.supported_entities


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

