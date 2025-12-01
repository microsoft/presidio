import logging
import os
from pathlib import Path
from typing import Optional

from presidio_analyzer.llm_utils import lx, load_yaml_file
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
        model_id: Optional[str] = None,
        config_path: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
        supported_language: str = "en",
    ):
        """
        Initialize Azure OpenAI LangExtract recognizer for PII/PHI detection.

        Note: Azure OpenAI endpoint and API configuration are not validated
        during initialization. Any connectivity or authentication issues will
        be reported when analyze() is first called.

        Configuration priority for authentication (highest to lowest):
        1. Direct parameters (azure_endpoint, api_key, api_version)
        2. Environment variables (AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION)
        
        Configuration priority for model_id (deployment name):
        1. Direct parameter (model_id)
        2. Config file (langextract.model.model_id)

        :param model_id: Azure OpenAI deployment name (e.g., "gpt-4", "gpt-4o"). Overrides config file.
        :param config_path: Path to YAML configuration file. If not provided, uses default config.
        :param azure_endpoint: Azure OpenAI endpoint URL (overrides env var).
        :param api_key: Azure OpenAI API key (overrides env var). If not provided, uses managed identity.
        :param api_version: Azure OpenAI API version (optional, defaults to "2024-02-15-preview").
        :param supported_language: Language this recognizer supports (optional, default: "en").
        :raises ImportError: If langextract is not installed.
        :raises ValueError: If Azure OpenAI endpoint is not provided via parameter or env var.
        """
        
        # Determine actual config path
        actual_config_path = (
            config_path if config_path else str(self.DEFAULT_CONFIG_PATH)
        )

        # Get Azure-specific settings with priority: parameter > env var
        self.azure_endpoint = (
            azure_endpoint 
            or os.environ.get("AZURE_OPENAI_ENDPOINT")
        )
        if not self.azure_endpoint:
            raise ValueError(
                "Azure OpenAI endpoint is required. Provide 'azure_endpoint' parameter "
                f"or set AZURE_OPENAI_ENDPOINT environment variable.\n"
                f"See {AZURE_OPENAI_DOCS_URL} for details."
            )

        self.api_key = (
            api_key
            or os.environ.get("AZURE_OPENAI_API_KEY")
        )
        # Note: If api_key is None, managed identity will be used

        self.api_version = (
            api_version
            or os.environ.get("AZURE_OPENAI_API_VERSION")
            or "2024-02-15-preview"
        )

        # Initialize parent class (loads config, sets self.model_id from config)
        super().__init__(
            config_path=actual_config_path,
            name="Azure OpenAI LangExtract PII",
            supported_language=supported_language
        )
        
        # Override model_id if provided as parameter (deployment name)
        if model_id:
            self.model_id = model_id

    def _call_langextract(self, **kwargs):
        """
        Call Azure OpenAI through LangExtract for PII extraction.

        Uses LangExtract's provider registry system to instantiate the custom
        Azure OpenAI provider. The model_id with 'azure:' prefix triggers the
        provider registration.
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
                "text_or_documents": kwargs.pop("text"),
                "prompt_description": kwargs.pop("prompt"),
                "examples": kwargs.pop("examples"),
                "model_id": model_id_with_prefix,
                "language_model_params": language_model_params,
                "fence_output": True,
                "use_schema_constraints": False,
            }
            
            extract_params.update(kwargs)

            return lx.extract(**extract_params)

        except Exception:
            logger.exception(
                "LangExtract extraction failed (Azure OpenAI at %s, model '%s')",
                self.azure_endpoint, self.model_id
            )
            raise
