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
    }):
        # Mock the classes and enums we need
        mock_deid_client = MagicMock()
        mock_default_cred = MagicMock()
        mock_managed_cred = MagicMock()
        
        # Mock TextEncodingType enum
        mock_text_encoding_type = MagicMock()
        mock_text_encoding_type.CODE_POINT = "CODE_POINT"
        
        # Mock DeidentificationOperationType enum
        mock_operation_type = MagicMock()
        mock_operation_type.SURROGATE_ONLY = "SURROGATE_ONLY"
        
        # Mock other required classes
        mock_tagged_entities = MagicMock()
        mock_deidentification_content = MagicMock()
        
        with patch('presidio_anonymizer.operators.ahds_surrogate.DeidentificationClient', mock_deid_client), \
             patch('presidio_anonymizer.operators.ahds_surrogate.DefaultAzureCredential', mock_default_cred), \
             patch('presidio_anonymizer.operators.ahds_surrogate.ManagedIdentityCredential', mock_managed_cred), \
             patch('presidio_anonymizer.operators.ahds_surrogate.TextEncodingType', mock_text_encoding_type), \
             patch('presidio_anonymizer.operators.ahds_surrogate.DeidentificationOperationType', mock_operation_type), \
             patch('presidio_anonymizer.operators.ahds_surrogate.TaggedPhiEntities', mock_tagged_entities), \
             patch('presidio_anonymizer.operators.ahds_surrogate.DeidentificationContent', mock_deidentification_content):
            yield {
                'DeidentificationClient': mock_deid_client,
                'DefaultAzureCredential': mock_default_cred,
                'ManagedIdentityCredential': mock_managed_cred,
                'TextEncodingType': mock_text_encoding_type,
                'DeidentificationOperationType': mock_operation_type,
                'TaggedPhiEntities': mock_tagged_entities,
                'DeidentificationContent': mock_deidentification_content,
            }


class TestAHDSCredentialSelection:
    """Test credential selection based on environment variables."""

    def test_uses_default_credential_in_development_environment(self, mock_azure_modules):
        """Test that DefaultAzureCredential is used when PRESIDIO_ENV=development."""
        operator = AHDSSurrogate()
        
        with patch.dict(os.environ, {'PRESIDIO_ENV': 'development', 'AHDS_ENDPOINT': 'https://test.endpoint.com'}):
            with patch.object(operator, '_convert_to_tagged_entities', return_value=[]):
                mock_client_instance = MagicMock()
                mock_result = MagicMock()
                mock_result.output_text = "anonymized text"
                mock_client_instance.deidentify_text.return_value = mock_result
                mock_azure_modules['DeidentificationClient'].return_value = mock_client_instance
                
                result = operator.operate("test text", {"entities": []})
                
                # Verify DefaultAzureCredential was called
                mock_azure_modules['DefaultAzureCredential'].assert_called_once()
                mock_azure_modules['ManagedIdentityCredential'].assert_not_called()
                
                # Verify DeidentificationClient was initialized with DefaultAzureCredential instance
                mock_azure_modules['DeidentificationClient'].assert_called_once()
                call_args = mock_azure_modules['DeidentificationClient'].call_args
                assert call_args[0][1] == mock_azure_modules['DefaultAzureCredential'].return_value

    def test_uses_managed_identity_in_production_environment(self, mock_azure_modules):
        """Test that ManagedIdentityCredential is used when PRESIDIO_ENV is not development."""
        operator = AHDSSurrogate()
        
        with patch.dict(os.environ, {'PRESIDIO_ENV': 'production', 'AHDS_ENDPOINT': 'https://test.endpoint.com'}):
            with patch.object(operator, '_convert_to_tagged_entities', return_value=[]):
                mock_client_instance = MagicMock()
                mock_result = MagicMock()
                mock_result.output_text = "anonymized text"
                mock_client_instance.deidentify_text.return_value = mock_result
                mock_azure_modules['DeidentificationClient'].return_value = mock_client_instance
                
                result = operator.operate("test text", {"entities": []})
                
                # Verify ManagedIdentityCredential was called
                mock_azure_modules['ManagedIdentityCredential'].assert_called_once()
                mock_azure_modules['DefaultAzureCredential'].assert_not_called()
                
                # Verify DeidentificationClient was initialized with ManagedIdentityCredential instance
                mock_azure_modules['DeidentificationClient'].assert_called_once()
                call_args = mock_azure_modules['DeidentificationClient'].call_args
                assert call_args[0][1] == mock_azure_modules['ManagedIdentityCredential'].return_value

    def test_uses_managed_identity_when_env_var_not_set(self, mock_azure_modules):
        """Test that ManagedIdentityCredential is used when PRESIDIO_ENV is not set."""
        operator = AHDSSurrogate()
        
        # Ensure PRESIDIO_ENV is not set
        env_without_presidio = {k: v for k, v in os.environ.items() if k != 'PRESIDIO_ENV'}
        env_without_presidio['AHDS_ENDPOINT'] = 'https://test.endpoint.com'
        
        with patch.dict(os.environ, env_without_presidio, clear=True):
            with patch.object(operator, '_convert_to_tagged_entities', return_value=[]):
                mock_client_instance = MagicMock()
                mock_result = MagicMock()
                mock_result.output_text = "anonymized text"
                mock_client_instance.deidentify_text.return_value = mock_result
                mock_azure_modules['DeidentificationClient'].return_value = mock_client_instance
                
                result = operator.operate("test text", {"entities": []})
                
                # Verify ManagedIdentityCredential was called
                mock_azure_modules['ManagedIdentityCredential'].assert_called_once()
                mock_azure_modules['DefaultAzureCredential'].assert_not_called()

    def test_uses_managed_identity_for_other_environment_values(self, mock_azure_modules):
        """Test that ManagedIdentityCredential is used for any PRESIDIO_ENV value other than 'development'."""
        operator = AHDSSurrogate()
        
        test_environments = ['prod', 'staging', 'test', 'Production', 'DEVELOPMENT', 'dev']
        
        for env_value in test_environments:
            with patch.dict(os.environ, {'PRESIDIO_ENV': env_value, 'AHDS_ENDPOINT': 'https://test.endpoint.com'}):
                with patch.object(operator, '_convert_to_tagged_entities', return_value=[]):
                    mock_client_instance = MagicMock()
                    mock_result = MagicMock()
                    mock_result.output_text = "anonymized text"
                    mock_client_instance.deidentify_text.return_value = mock_result
                    mock_azure_modules['DeidentificationClient'].return_value = mock_client_instance
                    
                    # Reset mocks
                    mock_azure_modules['DefaultAzureCredential'].reset_mock()
                    mock_azure_modules['ManagedIdentityCredential'].reset_mock()
                    mock_azure_modules['DeidentificationClient'].reset_mock()
                    
                    result = operator.operate("test text", {"entities": []})
                    
                    # Verify ManagedIdentityCredential was called for this environment
                    mock_azure_modules['ManagedIdentityCredential'].assert_called_once(), f"Failed for environment: {env_value}"
                    mock_azure_modules['DefaultAzureCredential'].assert_not_called(), f"DefaultAzureCredential should not be called for environment: {env_value}"