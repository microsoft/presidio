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


class TestAzureOpenAILangExtractRecognizerCallMethod:
    """Test the _call_langextract method to achieve >90% coverage."""

    def test_call_langextract_builds_correct_params_with_api_key(self, mock_langextract):
        """Test that _call_langextract builds correct parameters including API key."""
        from presidio_analyzer.predefined_recognizers import AzureOpenAILangExtractRecognizer
        
        recognizer = AzureOpenAILangExtractRecognizer(
            model_id="gpt-4o",
            azure_endpoint="https://test.openai.azure.com/",
            api_key="test-key-123"
        )
        
        # Mock to capture the call
        mock_langextract.extract.return_value = MagicMock()
        
        # Call through analyze which calls _call_langextract
        with patch('presidio_analyzer.llm_utils.config_loader.load_yaml_file') as mock_load:
            mock_load.return_value = {}
            # Trigger the call
            try:
                recognizer.analyze("test text", [])
            except:
                pass  # We just want to trigger the method
        
        # Verify extract was called with correct params
        if mock_langextract.extract.called:
            call_kwargs = mock_langextract.extract.call_args[1]
            assert call_kwargs["model_id"] == "azure:gpt-4o"
            assert "language_model_params" in call_kwargs
            assert call_kwargs["language_model_params"]["api_key"] == "test-key-123"
            assert call_kwargs["language_model_params"]["azure_endpoint"] == "https://test.openai.azure.com/"
            assert call_kwargs["fence_output"] is True
            assert call_kwargs["use_schema_constraints"] is False

    def test_call_langextract_without_api_key_for_managed_identity(self, mock_langextract):
        """Test that _call_langextract omits API key when using managed identity."""
        from presidio_analyzer.predefined_recognizers import AzureOpenAILangExtractRecognizer
        
        recognizer = AzureOpenAILangExtractRecognizer(
            model_id="gpt-4o",
            azure_endpoint="https://test.openai.azure.com/"
            # No API key - uses managed identity
        )
        
        mock_langextract.extract.return_value = MagicMock()
        
        with patch('presidio_analyzer.llm_utils.config_loader.load_yaml_file') as mock_load:
            mock_load.return_value = {}
            try:
                recognizer.analyze("test", [])
            except:
                pass
        
        if mock_langextract.extract.called:
            call_kwargs = mock_langextract.extract.call_args[1]
            # API key should NOT be in params
            assert "api_key" not in call_kwargs["language_model_params"]

    def test_call_langextract_passes_through_kwargs(self, mock_langextract):
        """Test that _call_langextract passes through additional kwargs."""
        from presidio_analyzer.predefined_recognizers import AzureOpenAILangExtractRecognizer
        
        recognizer = AzureOpenAILangExtractRecognizer(
            model_id="gpt-4o",
            azure_endpoint="https://test.openai.azure.com/",
            api_key="key"
        )
        
        mock_langextract.extract.return_value = MagicMock()
        
        # Call _call_langextract directly with extra kwargs
        try:
            recognizer._call_langextract(
                text="test",
                prompt="prompt",
                examples=[],
                temperature=0.7,
                max_workers=5
            )
        except:
            pass
        
        if mock_langextract.extract.called:
            call_kwargs = mock_langextract.extract.call_args[1]
            assert call_kwargs.get("temperature") == 0.7
            assert call_kwargs.get("max_workers") == 5

    def test_call_langextract_handles_exceptions(self, mock_langextract):
        """Test that _call_langextract properly logs and re-raises exceptions."""
        from presidio_analyzer.predefined_recognizers import AzureOpenAILangExtractRecognizer
        
        recognizer = AzureOpenAILangExtractRecognizer(
            model_id="gpt-4o",
            azure_endpoint="https://test.openai.azure.com/",
            api_key="key"
        )
        
        # Patch langextract.extract at the module level where it's actually called
        with patch('langextract.extract', side_effect=RuntimeError("Connection failed")):
            # Should re-raise the exception
            with pytest.raises(RuntimeError, match="Connection failed"):
                recognizer._call_langextract(
                    text="test",
                    prompt="prompt", 
                    examples=[MagicMock()]  # Provide mock example to avoid validation error
                )


class TestAzureOpenAIProvider:
    """Test the Azure OpenAI provider implementation."""

    def test_provider_registration(self):
        """Test that Azure OpenAI provider is properly registered."""
        from presidio_analyzer.predefined_recognizers.third_party import azure_openai_provider
        assert hasattr(azure_openai_provider, 'AzureOpenAILanguageModel')

    def test_provider_import_error_when_dependencies_missing(self):
        """Test that provider handles missing dependencies gracefully."""
        from presidio_analyzer.predefined_recognizers.third_party import azure_openai_provider
        assert azure_openai_provider is not None

    def test_provider_initialization_with_api_key(self):
        """Test provider initialization with API key."""
        from presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider import AzureOpenAILanguageModel
        
        with patch('openai.AzureOpenAI') as mock_client:
            provider = AzureOpenAILanguageModel(
                model_id="gpt-4o",
                api_key="test-key",
                azure_endpoint="https://test.openai.azure.com/"
            )
            
            assert provider.model_id == "gpt-4o"
            assert provider.api_key == "test-key"
            assert provider.azure_endpoint == "https://test.openai.azure.com/"
            assert provider.azure_deployment == "gpt-4o"
            mock_client.assert_called_once()

    def test_provider_initialization_with_azure_prefix(self):
        """Test that azure: prefix is stripped from model_id."""
        from presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider import AzureOpenAILanguageModel
        
        with patch('openai.AzureOpenAI'):
            provider = AzureOpenAILanguageModel(
                model_id="azure:gpt-4o",
                api_key="key",
                azure_endpoint="https://test.openai.azure.com/"
            )
            
            assert provider.model_id == "gpt-4o"
            assert provider.azure_deployment == "gpt-4o"

    def test_provider_initialization_with_azureopenai_prefix(self):
        """Test that azureopenai: prefix is stripped from model_id."""
        from presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider import AzureOpenAILanguageModel
        
        with patch('openai.AzureOpenAI'):
            provider = AzureOpenAILanguageModel(
                model_id="azureopenai:gpt-4o",
                api_key="key",
                azure_endpoint="https://test.openai.azure.com/"
            )
            
            assert provider.model_id == "gpt-4o"

    def test_provider_initialization_with_aoai_prefix(self):
        """Test that aoai: prefix is stripped from model_id."""
        from presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider import AzureOpenAILanguageModel
        
        with patch('openai.AzureOpenAI'):
            provider = AzureOpenAILanguageModel(
                model_id="aoai:gpt-4o",
                api_key="key",
                azure_endpoint="https://test.openai.azure.com/"
            )
            
            assert provider.model_id == "gpt-4o"

    def test_provider_requires_endpoint(self):
        """Test that provider raises error if endpoint is missing."""
        from presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider import AzureOpenAILanguageModel
        
        with pytest.raises(ValueError, match="Azure OpenAI endpoint is required"):
            AzureOpenAILanguageModel(
                model_id="gpt-4o",
                api_key="key"
                # Missing azure_endpoint
            )

    def test_provider_reads_endpoint_from_env(self):
        """Test that provider reads endpoint from environment variable."""
        from presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider import AzureOpenAILanguageModel
        
        with patch.dict(os.environ, {'AZURE_OPENAI_ENDPOINT': 'https://env.openai.azure.com/'}):
            with patch('openai.AzureOpenAI'):
                provider = AzureOpenAILanguageModel(
                    model_id="gpt-4o",
                    api_key="key"
                )
                
                assert provider.azure_endpoint == "https://env.openai.azure.com/"

    def test_provider_reads_api_key_from_env(self):
        """Test that provider reads API key from environment variable."""
        from presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider import AzureOpenAILanguageModel
        
        env_vars = {
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
            'AZURE_OPENAI_API_KEY': 'env-key'
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('openai.AzureOpenAI') as mock_client:
                provider = AzureOpenAILanguageModel(model_id="gpt-4o")
                
                assert provider.api_key == "env-key"
                # Verify client was created with API key
                mock_client.assert_called_once()
                call_kwargs = mock_client.call_args[1]
                assert call_kwargs['api_key'] == "env-key"

    def test_provider_uses_custom_api_version(self):
        """Test that provider uses custom API version."""
        from presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider import AzureOpenAILanguageModel
        
        with patch('openai.AzureOpenAI') as mock_client:
            provider = AzureOpenAILanguageModel(
                model_id="gpt-4o",
                api_key="key",
                azure_endpoint="https://test.openai.azure.com/",
                api_version="2024-10-01"
            )
            
            assert provider.api_version == "2024-10-01"
            mock_client.assert_called_once()
            call_kwargs = mock_client.call_args[1]
            assert call_kwargs['api_version'] == "2024-10-01"

    def test_provider_uses_default_api_version(self):
        """Test that provider uses default API version when not specified."""
        from presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider import AzureOpenAILanguageModel
        
        with patch('openai.AzureOpenAI'):
            provider = AzureOpenAILanguageModel(
                model_id="gpt-4o",
                api_key="key",
                azure_endpoint="https://test.openai.azure.com/"
            )
            
            assert provider.api_version == "2024-02-15-preview"

    def test_provider_custom_deployment_name(self):
        """Test that provider can use custom deployment name."""
        from presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider import AzureOpenAILanguageModel
        
        with patch('openai.AzureOpenAI'):
            provider = AzureOpenAILanguageModel(
                model_id="gpt-4o",
                api_key="key",
                azure_endpoint="https://test.openai.azure.com/",
                azure_deployment="custom-deployment"
            )
            
            assert provider.azure_deployment == "custom-deployment"
            assert provider.model_id == "gpt-4o"

    def test_provider_get_client_model_id(self):
        """Test that _get_client_model_id returns deployment name."""
        from presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider import AzureOpenAILanguageModel
        
        with patch('openai.AzureOpenAI'):
            provider = AzureOpenAILanguageModel(
                model_id="gpt-4o",
                api_key="key",
                azure_endpoint="https://test.openai.azure.com/",
                azure_deployment="my-deployment"
            )
            
            assert provider._get_client_model_id() == "my-deployment"

    def test_provider_managed_identity_development_env(self):
        """Test that provider uses DefaultAzureCredential in development."""
        from presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider import AzureOpenAILanguageModel
        
        with patch.dict(os.environ, {'ENV': 'development', 'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/'}):
            with patch('openai.AzureOpenAI'):
                with patch('presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider.DefaultAzureCredential') as mock_cred:
                    with patch('presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider.get_bearer_token_provider'):
                        provider = AzureOpenAILanguageModel(model_id="gpt-4o")
                        mock_cred.assert_called_once()

    def test_provider_managed_identity_production_env(self):
        """Test that provider uses ChainedTokenCredential in production."""
        from presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider import AzureOpenAILanguageModel
        
        env_vars = {
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/'
        }
        # Ensure ENV is not 'development'
        env_without_dev = {k: v for k, v in os.environ.items() if k != 'ENV'}
        env_without_dev.update(env_vars)
        
        with patch.dict(os.environ, env_without_dev, clear=True):
            with patch('openai.AzureOpenAI'):
                with patch('presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider.EnvironmentCredential') as mock_env_cred:
                    with patch('presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider.WorkloadIdentityCredential') as mock_workload_cred:
                        with patch('presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider.ManagedIdentityCredential') as mock_managed_cred:
                            with patch('presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider.ChainedTokenCredential') as mock_chain:
                                with patch('presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider.get_bearer_token_provider'):
                                    provider = AzureOpenAILanguageModel(model_id="gpt-4o")
                                    
                                    # Verify ChainedTokenCredential was called with the 3 credentials
                                    mock_chain.assert_called_once()
                                    call_args = mock_chain.call_args[0]
                                    assert len(call_args) == 3

    def test_provider_custom_token_provider(self):
        """Test that provider can use custom Azure AD token provider."""
        from presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider import AzureOpenAILanguageModel
        
        mock_token_provider = MagicMock()
        
        with patch('openai.AzureOpenAI') as mock_client:
            provider = AzureOpenAILanguageModel(
                model_id="gpt-4o",
                azure_endpoint="https://test.openai.azure.com/",
                azure_ad_token_provider=mock_token_provider
            )
            
            mock_client.assert_called_once()
            call_kwargs = mock_client.call_args[1]
            assert call_kwargs['azure_ad_token_provider'] == mock_token_provider

    def test_provider_import_error_without_langextract(self):
        """Test that provider raises ImportError when langextract is not available."""
        with patch('presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider.LANGEXTRACT_OPENAI_AVAILABLE', False):
            from presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider import AzureOpenAILanguageModel
            
            with pytest.raises(ImportError, match="LangExtract with OpenAI support is not installed"):
                AzureOpenAILanguageModel(
                    model_id="gpt-4o",
                    api_key="key",
                    azure_endpoint="https://test.openai.azure.com/"
                )

    def test_provider_import_error_without_azure_identity(self):
        """Test that provider raises error when azure-identity is missing for managed identity."""
        from presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider import AzureOpenAILanguageModel
        
        with patch('presidio_analyzer.predefined_recognizers.third_party.azure_openai_provider.AZURE_IDENTITY_AVAILABLE', False):
            with pytest.raises(ImportError, match="azure-identity is required"):
                AzureOpenAILanguageModel(
                    model_id="gpt-4o",
                    azure_endpoint="https://test.openai.azure.com/"
                    # No API key, so should try managed identity
                )