"""Tests for Azure authentication helper utilities."""

import os
from unittest.mock import MagicMock, patch


class TestGetAzureCredential:
    """Test get_azure_credential function."""

    @patch('presidio_analyzer.llm_utils.azure_auth_helper.DefaultAzureCredential')
    def test_when_development_env_then_uses_default_credential(self, mock_default_cred):
        """Test that development mode uses DefaultAzureCredential."""
        from presidio_analyzer.llm_utils.azure_auth_helper import get_azure_credential

        mock_cred_instance = MagicMock()
        mock_default_cred.return_value = mock_cred_instance

        with patch.dict(os.environ, {'ENV': 'development'}):
            credential = get_azure_credential()

        # Verify DefaultAzureCredential was called
        mock_default_cred.assert_called_once()
        assert credential == mock_cred_instance

    @patch('presidio_analyzer.llm_utils.azure_auth_helper.ChainedTokenCredential')
    @patch('presidio_analyzer.llm_utils.azure_auth_helper.EnvironmentCredential')
    @patch('presidio_analyzer.llm_utils.azure_auth_helper.WorkloadIdentityCredential')
    @patch('presidio_analyzer.llm_utils.azure_auth_helper.ManagedIdentityCredential')
    def test_when_production_env_then_uses_chained_credential(
        self, mock_managed, mock_workload, mock_env, mock_chained
    ):
        """Test that production mode uses ChainedTokenCredential."""
        from presidio_analyzer.llm_utils.azure_auth_helper import get_azure_credential

        mock_cred_instance = MagicMock()
        mock_chained.return_value = mock_cred_instance

        with patch.dict(os.environ, {'ENV': 'production'}):
            credential = get_azure_credential()

        # Verify ChainedTokenCredential was created with correct credentials
        mock_chained.assert_called_once()
        assert credential == mock_cred_instance

    @patch('presidio_analyzer.llm_utils.azure_auth_helper.ChainedTokenCredential')
    @patch('presidio_analyzer.llm_utils.azure_auth_helper.EnvironmentCredential')
    @patch('presidio_analyzer.llm_utils.azure_auth_helper.WorkloadIdentityCredential')
    @patch('presidio_analyzer.llm_utils.azure_auth_helper.ManagedIdentityCredential')
    def test_when_no_env_set_then_uses_chained_credential(
        self, mock_managed, mock_workload, mock_env, mock_chained
    ):
        """Test that missing ENV defaults to production mode."""
        from presidio_analyzer.llm_utils.azure_auth_helper import get_azure_credential

        mock_cred_instance = MagicMock()
        mock_chained.return_value = mock_cred_instance

        # Remove ENV from environment
        env = os.environ.copy()
        if 'ENV' in env:
            del env['ENV']

        with patch.dict(os.environ, env, clear=True):
            credential = get_azure_credential()

        # Verify ChainedTokenCredential was used (production mode)
        mock_chained.assert_called_once()
        assert credential == mock_cred_instance


class TestGetBearerTokenProvider:
    """Test get_bearer_token_provider_for_scope function."""

    @patch('azure.identity.get_bearer_token_provider')
    @patch('presidio_analyzer.llm_utils.azure_auth_helper.DefaultAzureCredential')
    def test_when_scope_provided_then_returns_provider(
        self, mock_default_cred, mock_get_provider
    ):
        """Test that token provider is created for a given scope."""
        from presidio_analyzer.llm_utils.azure_auth_helper import (
            get_bearer_token_provider_for_scope,
        )

        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider

        scope = "https://cognitiveservices.azure.com/.default"

        with patch.dict(os.environ, {'ENV': 'development'}):
            provider = get_bearer_token_provider_for_scope(scope)

        # Verify get_bearer_token_provider was called with scope
        mock_get_provider.assert_called_once()
        assert provider == mock_provider

    @patch('azure.identity.get_bearer_token_provider')
    def test_when_custom_credential_provided_then_uses_it(self, mock_get_provider):
        """Test that custom credential is used when provided."""
        from presidio_analyzer.llm_utils.azure_auth_helper import (
            get_bearer_token_provider_for_scope,
        )

        custom_credential = MagicMock()
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider

        scope = "https://cognitiveservices.azure.com/.default"
        provider = get_bearer_token_provider_for_scope(
            scope, credential=custom_credential
        )

        # Verify get_bearer_token_provider was called with custom credential
        mock_get_provider.assert_called_once_with(custom_credential, scope)
        assert provider == mock_provider
