"""Tests for AHDS Surrogate credential selection logic."""

import os
from unittest.mock import Mock, patch, MagicMock
import pytest

from presidio_anonymizer.operators import AHDSSurrogate
from presidio_anonymizer.entities import InvalidParamError


@pytest.fixture
def mock_azure_modules():
    """Mock Azure modules to avoid import dependencies."""
    with patch.dict('sys.modules', {
        'azure.health.deidentification': MagicMock(),
        'azure.identity': MagicMock(),
        'presidio_analyzer.llm_utils.azure_auth_helper': MagicMock(),
    }):
        # Mock the classes and enums we need
        mock_deid_client = MagicMock()
        mock_get_credential = MagicMock()
        
        # Mock TextEncodingType enum
        mock_text_encoding_type = MagicMock()
        mock_text_encoding_type.CODE_POINT = "CODE_POINT"
        
        # Mock DeidentificationOperationType enum
        mock_operation_type = MagicMock()
        mock_operation_type.SURROGATE_ONLY = "SURROGATE_ONLY"
        
        # Mock other required classes
        mock_tagged_entities = MagicMock()
        mock_customization_options = MagicMock()
        mock_deidentification_content = MagicMock()
        
        with patch('presidio_anonymizer.operators.ahds_surrogate.DeidentificationClient', mock_deid_client), \
             patch('presidio_anonymizer.operators.ahds_surrogate.get_azure_credential', mock_get_credential), \
             patch('presidio_anonymizer.operators.ahds_surrogate.TextEncodingType', mock_text_encoding_type), \
             patch('presidio_anonymizer.operators.ahds_surrogate.DeidentificationOperationType', mock_operation_type), \
             patch('presidio_anonymizer.operators.ahds_surrogate.TaggedPhiEntities', mock_tagged_entities), \
             patch('presidio_anonymizer.operators.ahds_surrogate.DeidentificationContent', mock_deidentification_content), \
             patch('presidio_anonymizer.operators.ahds_surrogate.DeidentificationCustomizationOptions', mock_customization_options):
            yield {
                'DeidentificationClient': mock_deid_client,
                'get_azure_credential': mock_get_credential,
                'TextEncodingType': mock_text_encoding_type,
                'DeidentificationOperationType': mock_operation_type,
                'TaggedPhiEntities': mock_tagged_entities,
                'DeidentificationContent': mock_deidentification_content,
                'DeidentificationCustomizationOptions': mock_customization_options,
            }


class TestAHDSCredentialSelection:
    """Test credential selection based on environment variables."""

    def test_uses_default_credential_in_development_environment(self, mock_azure_modules):
        """Test that get_azure_credential is called (which uses DefaultAzureCredential for ENV=development)."""
        operator = AHDSSurrogate()
        
        with patch.dict(os.environ, {'ENV': 'development', 'AHDS_ENDPOINT': 'https://test.endpoint.com'}):
            with patch.object(operator, '_convert_to_tagged_entities', return_value=[]):
                mock_client_instance = MagicMock()
                mock_result = MagicMock()
                mock_result.output_text = "anonymized text"
                mock_client_instance.deidentify_text.return_value = mock_result
                mock_azure_modules['DeidentificationClient'].return_value = mock_client_instance
                mock_credential = MagicMock()
                mock_azure_modules['get_azure_credential'].return_value = mock_credential
                
                result = operator.operate("test text", {"entities": []})
                
                # Verify get_azure_credential was called
                mock_azure_modules['get_azure_credential'].assert_called_once()
                
                # Verify DeidentificationClient was initialized with credential from helper
                mock_azure_modules['DeidentificationClient'].assert_called_once()
                call_args = mock_azure_modules['DeidentificationClient'].call_args
                assert call_args[0][1] == mock_credential

    def test_uses_chained_credential_in_production_environment(self, mock_azure_modules):
        """Test that get_azure_credential is called (which uses ChainedTokenCredential for ENV=production)."""
        operator = AHDSSurrogate()
        
        with patch.dict(os.environ, {'ENV': 'production', 'AHDS_ENDPOINT': 'https://test.endpoint.com'}):
            with patch.object(operator, '_convert_to_tagged_entities', return_value=[]):
                mock_client_instance = MagicMock()
                mock_result = MagicMock()
                mock_result.output_text = "anonymized text"
                mock_client_instance.deidentify_text.return_value = mock_result
                mock_azure_modules['DeidentificationClient'].return_value = mock_client_instance
                mock_credential = MagicMock()
                mock_azure_modules['get_azure_credential'].return_value = mock_credential
                
                result = operator.operate("test text", {"entities": []})
                
                # Verify get_azure_credential was called
                mock_azure_modules['get_azure_credential'].assert_called_once()
                
                # Verify DeidentificationClient was initialized with credential from helper
                call_args = mock_azure_modules['DeidentificationClient'].call_args
                assert call_args[0][1] == mock_credential

    def test_uses_chained_credential_when_env_var_not_set(self, mock_azure_modules):
        """Test that get_azure_credential is called when ENV is not set (defaults to production mode)."""
        operator = AHDSSurrogate()
        
        # Ensure ENV is not set
        env_without_presidio = {k: v for k, v in os.environ.items() if k != 'ENV'}
        env_without_presidio['AHDS_ENDPOINT'] = 'https://test.endpoint.com'
        
        with patch.dict(os.environ, env_without_presidio, clear=True):
            with patch.object(operator, '_convert_to_tagged_entities', return_value=[]):
                mock_client_instance = MagicMock()
                mock_result = MagicMock()
                mock_result.output_text = "anonymized text"
                mock_client_instance.deidentify_text.return_value = mock_result
                mock_azure_modules['DeidentificationClient'].return_value = mock_client_instance
                mock_credential = MagicMock()
                mock_azure_modules['get_azure_credential'].return_value = mock_credential
                
                result = operator.operate("test text", {"entities": []})
                
                # Verify get_azure_credential was called
                mock_azure_modules['get_azure_credential'].assert_called_once()

    def test_uses_chained_credential_for_non_development_environment_values(self, mock_azure_modules):
        """Test that get_azure_credential is called for any ENV value (delegates to helper)."""
        operator = AHDSSurrogate()
        
        test_environments = ['prod', 'production', 'staging', 'test', 'local', 'DEVELOPMENT']
        
        for env_value in test_environments:
            with patch.dict(os.environ, {'ENV': env_value, 'AHDS_ENDPOINT': 'https://test.endpoint.com'}):
                with patch.object(operator, '_convert_to_tagged_entities', return_value=[]):
                    mock_client_instance = MagicMock()
                    mock_result = MagicMock()
                    mock_result.output_text = "anonymized text"
                    mock_client_instance.deidentify_text.return_value = mock_result
                    mock_azure_modules['DeidentificationClient'].return_value = mock_client_instance
                    mock_credential = MagicMock()
                    mock_azure_modules['get_azure_credential'].return_value = mock_credential
                    
                    # Reset mocks
                    mock_azure_modules['get_azure_credential'].reset_mock()
                    mock_azure_modules['DeidentificationClient'].reset_mock()
                    
                    result = operator.operate("test text", {"entities": []})
                    
                    # Verify get_azure_credential was called
                    mock_azure_modules['get_azure_credential'].assert_called_once(), f"Failed for environment: {env_value}"