"""Tests for AHDS Recognizer credential selection logic."""

import os
from unittest.mock import Mock, patch, MagicMock
import pytest

from presidio_analyzer.predefined_recognizers.third_party.ahds_recognizer import AzureHealthDeidRecognizer


@pytest.fixture
def mock_azure_modules():
    """Mock Azure modules to avoid import dependencies."""
    with patch.dict('sys.modules', {
        'azure.health.deidentification': MagicMock(),
        'azure.identity': MagicMock(),
    }):
        # Mock the classes we need
        mock_deid_client = MagicMock()
        mock_default_cred = MagicMock()
        mock_managed_cred = MagicMock()
        
        with patch('presidio_analyzer.predefined_recognizers.third_party.ahds_recognizer.DeidentificationClient', mock_deid_client), \
             patch('presidio_analyzer.predefined_recognizers.third_party.ahds_recognizer.DefaultAzureCredential', mock_default_cred), \
             patch('presidio_analyzer.predefined_recognizers.third_party.ahds_recognizer.ManagedIdentityCredential', mock_managed_cred):
            yield {
                'DeidentificationClient': mock_deid_client,
                'DefaultAzureCredential': mock_default_cred,
                'ManagedIdentityCredential': mock_managed_cred,
            }


class TestAHDSRecognizerCredentialSelection:
    """Test credential selection based on environment variables."""

    def test_uses_default_credential_in_development_environment(self, mock_azure_modules):
        """Test that DefaultAzureCredential is used when PRESIDIO_ENV=development."""
        with patch.dict(os.environ, {'PRESIDIO_ENV': 'development', 'AHDS_ENDPOINT': 'https://test.endpoint.com'}):
            mock_client_instance = MagicMock()
            mock_azure_modules['DeidentificationClient'].return_value = mock_client_instance
            
            recognizer = AzureHealthDeidRecognizer()
            
            # Verify DefaultAzureCredential was called
            mock_azure_modules['DefaultAzureCredential'].assert_called_once()
            mock_azure_modules['ManagedIdentityCredential'].assert_not_called()
            
            # Verify DeidentificationClient was initialized with DefaultAzureCredential instance
            mock_azure_modules['DeidentificationClient'].assert_called_once()
            call_args = mock_azure_modules['DeidentificationClient'].call_args
            assert call_args[0][1] == mock_azure_modules['DefaultAzureCredential'].return_value

    def test_uses_managed_identity_in_production_environment(self, mock_azure_modules):
        """Test that ManagedIdentityCredential is used when PRESIDIO_ENV is not development."""
        with patch.dict(os.environ, {'PRESIDIO_ENV': 'production', 'AHDS_ENDPOINT': 'https://test.endpoint.com'}):
            mock_client_instance = MagicMock()
            mock_azure_modules['DeidentificationClient'].return_value = mock_client_instance
            
            recognizer = AzureHealthDeidRecognizer()
            
            # Verify ManagedIdentityCredential was called
            mock_azure_modules['ManagedIdentityCredential'].assert_called_once()
            mock_azure_modules['DefaultAzureCredential'].assert_not_called()
            
            # Verify DeidentificationClient was initialized with ManagedIdentityCredential instance
            mock_azure_modules['DeidentificationClient'].assert_called_once()
            call_args = mock_azure_modules['DeidentificationClient'].call_args
            assert call_args[0][1] == mock_azure_modules['ManagedIdentityCredential'].return_value

    def test_uses_managed_identity_when_env_var_not_set(self, mock_azure_modules):
        """Test that ManagedIdentityCredential is used when PRESIDIO_ENV is not set."""
        # Ensure PRESIDIO_ENV is not set
        env_without_presidio = {k: v for k, v in os.environ.items() if k != 'PRESIDIO_ENV'}
        env_without_presidio['AHDS_ENDPOINT'] = 'https://test.endpoint.com'
        
        with patch.dict(os.environ, env_without_presidio, clear=True):
            mock_client_instance = MagicMock()
            mock_azure_modules['DeidentificationClient'].return_value = mock_client_instance
            
            recognizer = AzureHealthDeidRecognizer()
            
            # Verify ManagedIdentityCredential was called
            mock_azure_modules['ManagedIdentityCredential'].assert_called_once()
            mock_azure_modules['DefaultAzureCredential'].assert_not_called()

    def test_uses_managed_identity_for_other_environment_values(self, mock_azure_modules):
        """Test that ManagedIdentityCredential is used for any PRESIDIO_ENV value other than 'development'."""
        test_environments = ['prod', 'staging', 'test', 'Production', 'DEVELOPMENT', 'dev']
        
        for env_value in test_environments:
            with patch.dict(os.environ, {'PRESIDIO_ENV': env_value, 'AHDS_ENDPOINT': 'https://test.endpoint.com'}):
                mock_client_instance = MagicMock()
                mock_azure_modules['DeidentificationClient'].return_value = mock_client_instance
                
                # Reset mocks
                mock_azure_modules['DefaultAzureCredential'].reset_mock()
                mock_azure_modules['ManagedIdentityCredential'].reset_mock()
                mock_azure_modules['DeidentificationClient'].reset_mock()
                
                recognizer = AzureHealthDeidRecognizer()
                
                # Verify ManagedIdentityCredential was called for this environment
                mock_azure_modules['ManagedIdentityCredential'].assert_called_once(), f"Failed for environment: {env_value}"
                mock_azure_modules['DefaultAzureCredential'].assert_not_called(), f"DefaultAzureCredential should not be called for environment: {env_value}"

    def test_respects_provided_client_parameter(self, mock_azure_modules):
        """Test that when a client is provided, no credential creation occurs."""
        mock_client_instance = MagicMock()
        
        with patch.dict(os.environ, {'PRESIDIO_ENV': 'development', 'AHDS_ENDPOINT': 'https://test.endpoint.com'}):
            recognizer = AzureHealthDeidRecognizer(client=mock_client_instance)
            
            # Verify no credential classes were called
            mock_azure_modules['DefaultAzureCredential'].assert_not_called()
            mock_azure_modules['ManagedIdentityCredential'].assert_not_called()
            mock_azure_modules['DeidentificationClient'].assert_not_called()
            
            # Verify the provided client is used
            assert recognizer.deid_client == mock_client_instance