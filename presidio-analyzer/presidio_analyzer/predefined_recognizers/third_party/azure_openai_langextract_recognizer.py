"""
Azure OpenAI LangExtract Recognizer for Presidio.

This module provides a concrete implementation of the LangExtract recognizer
using Azure OpenAI as the backend LLM provider.

Implementation based on:
- PR #1775 (Ollama LangExtract pattern)
- LangExtract PR #38 (Azure OpenAI provider pattern)
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

try:
    import langextract as lx
    LANGEXTRACT_AVAILABLE = True
except ImportError:
    LANGEXTRACT_AVAILABLE = False
    lx = None

from presidio_analyzer.predefined_recognizers.third_party.langextract_recognizer import (
    LangExtractRecognizer,
)

logger = logging.getLogger("presidio-analyzer")

AZURE_OPENAI_DOCS_URL = "https://learn.microsoft.com/en-us/azure/ai-services/openai/"


class AzureOpenAILangExtractRecognizer(LangExtractRecognizer):
    """
    Concrete implementation of LangExtract recognizer using Azure OpenAI backend.

    Provides Azure OpenAI-specific functionality including:
    - Azure OpenAI endpoint and API key configuration
    - Deployment name management
    - API version control
    - Integration with custom Azure OpenAI provider via LangExtract registry
    """

    DEFAULT_CONFIG_PATH = (
        Path(__file__).parent.parent.parent / "conf" / "langextract_config_azureopenai.yaml"
    )

    def __init__(
        self,
        config_path: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        """
        Initialize Azure OpenAI LangExtract recognizer for PII/PHI detection.

        Configuration priority (highest to lowest):
        1. Direct parameters (azure_endpoint, api_key, api_version)
        2. Environment variables (AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION)
        3. Config file (azure_openai section)
        
        Authentication and connectivity are not validated during initialization.
        Any issues will be reported when analyze() is first called.

        :param config_path: Path to YAML configuration file. If not provided, uses default config.
        :param azure_endpoint: Azure OpenAI endpoint URL (overrides config and env var).
        :param api_key: Azure OpenAI API key (overrides config and env var).
        :param api_version: Azure OpenAI API version (overrides config and env var).
        """
        if not LANGEXTRACT_AVAILABLE:
            raise ImportError(
                "LangExtract is not installed. "
                "Install it with: pip install presidio-analyzer[langextract] "
                "or: pip install langextract"
            )
        
        # Determine actual config path
        actual_config_path = (
            config_path if config_path else str(self.DEFAULT_CONFIG_PATH)
        )

        try:
            super().__init__(
                config_path=actual_config_path,
                name="Azure OpenAI LangExtract PII"
            )

            # Load Azure-specific configuration from the config file
            azure_config = self._load_azure_openai_config(actual_config_path)
            
            # Get Azure-specific settings with priority: parameter > env var > config file
            self.azure_endpoint = (
                azure_endpoint 
                or os.environ.get("AZURE_OPENAI_ENDPOINT")
                or azure_config.get("azure_endpoint")
            )
            if not self.azure_endpoint:
                raise ValueError(
                    "Azure OpenAI endpoint is required. Provide 'azure_endpoint' parameter, "
                    "set AZURE_OPENAI_ENDPOINT environment variable, or configure "
                    "'azure_endpoint' in config file."
                )

            self.api_key = (
                api_key
                or os.environ.get("AZURE_OPENAI_API_KEY")
                or azure_config.get("api_key")
            )

            self.api_version = (
                api_version
                or os.environ.get("AZURE_OPENAI_API_VERSION")
                or azure_config.get("api_version")
                or "2024-02-15-preview"
            )
            
            # Note: self.model_id and self.temperature are already set by parent class from langextract.model config
            
        except Exception:
            logger.exception(
                "Failed to initialize Azure OpenAI LangExtract recognizer. "
                "Check that configuration file exists and is valid, Azure endpoint is configured, "
                "and that required dependencies (langextract, Jinja2) are installed."
            )
            raise

    def _load_azure_openai_config(self, config_path: str) -> Dict:
        """
        Load Azure OpenAI-specific configuration.

        :param config_path: Path to configuration file.
        :return: Azure OpenAI configuration dictionary.
        """
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}"
            )

        import yaml
        with open(config_path, 'r') as f:
            full_config = yaml.safe_load(f)

        azure_config = full_config.get("azure_openai", {})

        if not azure_config:
            raise ValueError(
                "Configuration file must contain 'azure_openai' section "
                "with Azure OpenAI-specific config"
            )

        return azure_config

    def _validate_llm_availability(self) -> bool:
        """
        Validate Azure OpenAI service availability.

        :return: True (assumes service is available if configured).
        """
        return True

    def _call_langextract(
        self,
        text: str,
        prompt: str,
        examples: List,
        **kwargs
    ):
        """
        Call Azure OpenAI through LangExtract for PII extraction.

        Uses LangExtract's provider registry system to instantiate the custom
        Azure OpenAI provider. The model_id with 'azure:' prefix triggers the
        provider registration.

        :param text: Text to analyze.
        :param prompt: Prompt description for LangExtract.
        :param examples: LangExtract examples.
        :param kwargs: Additional parameters.
        :return: LangExtract result object.
        """
        try:
            from presidio_analyzer.predefined_recognizers.third_party import (
                azure_openai_provider
            )

            model_id_with_prefix = f"azure:{self.model_id}"

            language_model_params = {
                "azure_endpoint": self.azure_endpoint,
                "api_version": self.api_version,
                "azure_deployment": self.model_id,
            }
            
            if self.api_key:
                language_model_params["api_key"] = self.api_key

            extract_params = {
                "text_or_documents": text,
                "prompt_description": prompt,
                "examples": examples,
                "model_id": model_id_with_prefix,
                "language_model_params": language_model_params,
                "fence_output": True,
                "use_schema_constraints": False,
            }
            
            if self.temperature is not None:
                extract_params["temperature"] = self.temperature

            extract_params.update(kwargs)

            return lx.extract(**extract_params)

        except Exception as e:
            logger.error(f"Error calling Azure OpenAI: {e}")
            raise
            raise
