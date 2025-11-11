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
        mock_chained_cred = MagicMock()
        mock_env_cred = MagicMock()
        mock_workload_cred = MagicMock()
        mock_managed_cred = MagicMock()
        
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
             patch('presidio_anonymizer.operators.ahds_surrogate.DefaultAzureCredential', mock_default_cred), \
             patch('presidio_anonymizer.operators.ahds_surrogate.ChainedTokenCredential', mock_chained_cred), \
             patch('presidio_anonymizer.operators.ahds_surrogate.EnvironmentCredential', mock_env_cred), \
             patch('presidio_anonymizer.operators.ahds_surrogate.WorkloadIdentityCredential', mock_workload_cred), \
             patch('presidio_anonymizer.operators.ahds_surrogate.ManagedIdentityCredential', mock_managed_cred), \
             patch('presidio_anonymizer.operators.ahds_surrogate.TextEncodingType', mock_text_encoding_type), \
             patch('presidio_anonymizer.operators.ahds_surrogate.DeidentificationOperationType', mock_operation_type), \
             patch('presidio_anonymizer.operators.ahds_surrogate.TaggedPhiEntities', mock_tagged_entities), \
             patch('presidio_anonymizer.operators.ahds_surrogate.DeidentificationContent', mock_deidentification_content), \
             patch('presidio_anonymizer.operators.ahds_surrogate.DeidentificationCustomizationOptions', mock_customization_options):
            yield {
                'DeidentificationClient': mock_deid_client,
                'DefaultAzureCredential': mock_default_cred,
                'ChainedTokenCredential': mock_chained_cred,
                'EnvironmentCredential': mock_env_cred,
                'WorkloadIdentityCredential': mock_workload_cred,
                'ManagedIdentityCredential': mock_managed_cred,
                'TextEncodingType': mock_text_encoding_type,
                'DeidentificationOperationType': mock_operation_type,
                'TaggedPhiEntities': mock_tagged_entities,
                'DeidentificationContent': mock_deidentification_content,
                'DeidentificationCustomizationOptions': mock_customization_options,
            }


class TestAHDSCredentialSelection:
    """Test credential selection based on environment variables."""

    def test_uses_default_credential_in_development_environment(self, mock_azure_modules):
        """Test that DefaultAzureCredential is used when ENV=development."""
        operator = AHDSSurrogate()
        
        with patch.dict(os.environ, {'ENV': 'development', 'AHDS_ENDPOINT': 'https://test.endpoint.com'}):
            with patch.object(operator, '_convert_to_tagged_entities', return_value=[]):
                mock_client_instance = MagicMock()
                mock_result = MagicMock()
                mock_result.output_text = "anonymized text"
                mock_client_instance.deidentify_text.return_value = mock_result
                mock_azure_modules['DeidentificationClient'].return_value = mock_client_instance
                
                result = operator.operate("test text", {"entities": []})
                
                # Verify DefaultAzureCredential was called
                mock_azure_modules['DefaultAzureCredential'].assert_called_once()
                mock_azure_modules['ChainedTokenCredential'].assert_not_called()
                
                # Verify DeidentificationClient was initialized with DefaultAzureCredential instance
                mock_azure_modules['DeidentificationClient'].assert_called_once()
                call_args = mock_azure_modules['DeidentificationClient'].call_args
                assert call_args[0][1] == mock_azure_modules['DefaultAzureCredential'].return_value

    def test_uses_chained_credential_in_production_environment(self, mock_azure_modules):
        """Test that ChainedTokenCredential is used when ENV=production."""
        operator = AHDSSurrogate()
        
        with patch.dict(os.environ, {'ENV': 'production', 'AHDS_ENDPOINT': 'https://test.endpoint.com'}):
            with patch.object(operator, '_convert_to_tagged_entities', return_value=[]):
                mock_client_instance = MagicMock()
                mock_result = MagicMock()
                mock_result.output_text = "anonymized text"
                mock_client_instance.deidentify_text.return_value = mock_result
                mock_azure_modules['DeidentificationClient'].return_value = mock_client_instance
                
                result = operator.operate("test text", {"entities": []})
                
                # Verify ChainedTokenCredential was called with the right credentials
                mock_azure_modules['EnvironmentCredential'].assert_called_once()
                mock_azure_modules['WorkloadIdentityCredential'].assert_called_once()
                mock_azure_modules['ManagedIdentityCredential'].assert_called_once()
                mock_azure_modules['ChainedTokenCredential'].assert_called_once()
                mock_azure_modules['DefaultAzureCredential'].assert_not_called()
                
                # Verify ChainedTokenCredential was called with correct order
                call_args = mock_azure_modules['ChainedTokenCredential'].call_args[0]
                assert call_args[0] == mock_azure_modules['EnvironmentCredential'].return_value
                assert call_args[1] == mock_azure_modules['WorkloadIdentityCredential'].return_value
                assert call_args[2] == mock_azure_modules['ManagedIdentityCredential'].return_value

    def test_uses_chained_credential_when_env_var_not_set(self, mock_azure_modules):
        """Test that ChainedTokenCredential is used when ENV is not set (default)."""
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
                
                result = operator.operate("test text", {"entities": []})
                
                # Verify ChainedTokenCredential was called (secure by default)
                mock_azure_modules['ChainedTokenCredential'].assert_called_once()
                mock_azure_modules['DefaultAzureCredential'].assert_not_called()

    def test_uses_chained_credential_for_non_development_environment_values(self, mock_azure_modules):
        """Test that ChainedTokenCredential is used for any ENV value other than 'development'."""
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
                    
                    # Reset mocks
                    mock_azure_modules['DefaultAzureCredential'].reset_mock()
                    mock_azure_modules['ChainedTokenCredential'].reset_mock()
                    mock_azure_modules['EnvironmentCredential'].reset_mock()
                    mock_azure_modules['WorkloadIdentityCredential'].reset_mock()
                    mock_azure_modules['ManagedIdentityCredential'].reset_mock()
                    mock_azure_modules['DeidentificationClient'].reset_mock()
                    
                    result = operator.operate("test text", {"entities": []})
                    
                    # Verify ChainedTokenCredential was called for this environment
                    mock_azure_modules['ChainedTokenCredential'].assert_called_once(), f"Failed for environment: {env_value}"
                    mock_azure_modules['DefaultAzureCredential'].assert_not_called(), f"DefaultAzureCredential should not be called for environment: {env_value}"