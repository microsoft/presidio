import logging
import os
from pathlib import Path
from typing import Optional

try:
    import langextract as lx
    import openai
    from langextract.providers.openai import OpenAILanguageModel
    LANGEXTRACT_OPENAI_AVAILABLE = True
except ImportError:  # pragma: no cover
    LANGEXTRACT_OPENAI_AVAILABLE = False
    lx = None
    OpenAILanguageModel = None
    openai = None

try:
    from azure.identity import (
        ChainedTokenCredential,
        DefaultAzureCredential,
        EnvironmentCredential,
        ManagedIdentityCredential,
        WorkloadIdentityCredential,
        get_bearer_token_provider,
    )
    AZURE_IDENTITY_AVAILABLE = True
except ImportError:  # pragma: no cover
    AZURE_IDENTITY_AVAILABLE = False
    ChainedTokenCredential = None
    DefaultAzureCredential = None
    EnvironmentCredential = None
    ManagedIdentityCredential = None
    WorkloadIdentityCredential = None
    get_bearer_token_provider = None

from presidio_analyzer.predefined_recognizers.third_party import (
    langextract_recognizer,
)

logger = logging.getLogger("presidio-analyzer")

LangExtractRecognizer = langextract_recognizer.LangExtractRecognizer

AZURE_OPENAI_DOCS_URL = "https://learn.microsoft.com/en-us/azure/ai-services/openai/"


# Azure OpenAI Provider for LangExtract
# This is an internal implementation detail used by the recognizer below

if LANGEXTRACT_OPENAI_AVAILABLE:
    class AzureOpenAILanguageModel(OpenAILanguageModel):
        """
        Custom LangExtract provider for Azure OpenAI.

        This provider extends OpenAILanguageModel to support Azure-specific
        authentication and endpoint configuration. It reuses all inference logic
        from the parent class and only overrides client initialization.

        Supports model_id patterns like:
        - Direct deployment name: "gpt-4o"
        - With prefix: "azure:gpt-4o" or "azureopenai:gpt-4o"
        """

        def __init__(
            self,
            model_id: str,
            api_key: Optional[str] = None,
            azure_endpoint: Optional[str] = None,
            api_version: Optional[str] = None,
            azure_deployment: Optional[str] = None,
            azure_ad_token_provider: Optional[any] = None,
            **kwargs
        ):
            """
            Initialize Azure OpenAI provider.

            :param model_id: Azure OpenAI deployment name or model identifier.
            :param api_key: Azure OpenAI API key (or set AZURE_OPENAI_API_KEY
                env var). If not provided, will automatically use managed
                identity (ChainedTokenCredential).
            :param azure_endpoint: Azure OpenAI endpoint URL
                (or set AZURE_OPENAI_ENDPOINT env var).
            :param api_version: Azure OpenAI API version
                (or set AZURE_OPENAI_API_VERSION env var).
            :param azure_deployment: Explicit deployment name (optional,
                defaults to model_id).
            :param azure_ad_token_provider: Custom Azure AD token provider function.
            :param kwargs: Additional parameters passed to parent class.
            """
            if not LANGEXTRACT_OPENAI_AVAILABLE:
                raise ImportError(
                    "LangExtract with OpenAI support is not installed. "
                    "Install it with: pip install presidio-analyzer[langextract] "
                    "or: pip install langextract[openai]"
                )

            clean_model_id = model_id
            for prefix in ["azure:", "azureopenai:", "aoai:"]:
                if model_id.lower().startswith(prefix):
                    clean_model_id = model_id[len(prefix):]
                    break

            self.model_id = clean_model_id
            self.api_key = api_key or os.environ.get("AZURE_OPENAI_API_KEY")
            self.organization = None
            self.format_type = kwargs.get('format_type', lx.data.FormatType.JSON)
            self.temperature = kwargs.get('temperature', 0.0)
            self.max_workers = kwargs.get('max_workers', 10)
            self._extra_kwargs = kwargs

            # Azure-specific configuration
            self.azure_endpoint = azure_endpoint or os.environ.get(
                "AZURE_OPENAI_ENDPOINT"
            )
            self.api_version = api_version or os.environ.get(
                "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
            )
            self.azure_deployment = azure_deployment or clean_model_id

            if not self.azure_endpoint:
                raise ValueError(
                    "Azure OpenAI endpoint is required. Set AZURE_OPENAI_ENDPOINT "
                    "environment variable or pass azure_endpoint parameter."
                )

            if not self.api_key or azure_ad_token_provider:
                if not AZURE_IDENTITY_AVAILABLE and not azure_ad_token_provider:
                    raise ImportError(
                        "azure-identity is required for managed identity "
                        "authentication. Install it with: pip install azure-identity"
                    )

                if azure_ad_token_provider:
                    token_provider = azure_ad_token_provider
                    credential_type = "custom token provider"
                else:
                    if os.getenv('ENV') == 'development':
                        credential = DefaultAzureCredential()
                        credential_type = "DefaultAzureCredential (development)"
                    else:
                        credential = ChainedTokenCredential(
                            EnvironmentCredential(),
                            WorkloadIdentityCredential(),
                            ManagedIdentityCredential()
                        )
                        credential_type = "ChainedTokenCredential"

                    token_provider = get_bearer_token_provider(
                        credential,
                        "https://cognitiveservices.azure.com/.default"
                    )

                self._client = openai.AzureOpenAI(
                    azure_ad_token_provider=token_provider,
                    azure_endpoint=self.azure_endpoint,
                    api_version=self.api_version
                )

                logger.debug(
                    f"Initialized Azure OpenAI provider with {credential_type}"
                )
            else:
                self._client = openai.AzureOpenAI(
                    api_key=self.api_key,
                    azure_endpoint=self.azure_endpoint,
                    api_version=self.api_version
                )

                logger.debug(
                    "Initialized Azure OpenAI provider with API key authentication"
                )

        def _get_client_model_id(self) -> str:
            """
            Return the model/deployment identifier for API calls.

            For Azure OpenAI, this is the deployment name, not the base model name.

            :return: Azure deployment name.
            """
            return self.azure_deployment
else:  # pragma: no cover
    class AzureOpenAILanguageModel:
        """Placeholder when langextract is not installed."""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "LangExtract with OpenAI support is not installed. "
                "Install it with: pip install presidio-analyzer[langextract,openai] "
                "or: pip install langextract[openai]"
            )


# Register the provider with LangExtract
if LANGEXTRACT_OPENAI_AVAILABLE:
    try:
        @lx.providers.registry.register(
            r'^azure:',
            r'^azureopenai:',
            r'^aoai:',
            priority=20
        )
        class RegisteredAzureOpenAILanguageModel(AzureOpenAILanguageModel):
            """
            Registered version of Azure OpenAI provider for LangExtract.

            This class is automatically discovered by LangExtract's provider registry
            and used when model_id matches any of the registered patterns.
            """

            pass

        logger.debug("Azure OpenAI provider registered with LangExtract")
    except Exception as e:  # pragma: no cover
        logger.error(f"Failed to register Azure OpenAI provider: {e}")
        raise


class AzureOpenAILangExtractRecognizer(LangExtractRecognizer):
    """
    Concrete implementation of LangExtract recognizer using Azure OpenAI backend.

    Provides Azure OpenAI-specific functionality including:
    - Azure OpenAI endpoint and API key configuration
    - Deployment name management
    - API version control
    - Integration with custom Azure OpenAI provider via LangExtract registry
    """

    DEFAULT_API_VERSION = "2024-02-15-preview"

    DEFAULT_CONFIG_PATH = (
        Path(__file__).parent.parent.parent
        / "conf"
        / "langextract_config_azureopenai.yaml"
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
        2. Environment variables (AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY,
           AZURE_OPENAI_API_VERSION)

        Configuration priority for model_id (deployment name):
        1. Direct parameter (model_id)
        2. Config file (langextract.model.model_id)

        :param model_id: Azure OpenAI deployment name (e.g., "gpt-4",
            "gpt-4o"). Overrides config file.
        :param config_path: Path to YAML configuration file. If not provided,
            uses default config.
        :param azure_endpoint: Azure OpenAI endpoint URL (overrides env var).
        :param api_key: Azure OpenAI API key (overrides env var). If not
            provided, uses managed identity.
        :param api_version: Azure OpenAI API version (optional, defaults to
            "2024-02-15-preview").
        :param supported_language: Language this recognizer supports
            (optional, default: "en").
        :raises ImportError: If langextract is not installed.
        :raises ValueError: If Azure OpenAI endpoint is not provided via
            parameter or env var.
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
            or self.DEFAULT_API_VERSION
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
