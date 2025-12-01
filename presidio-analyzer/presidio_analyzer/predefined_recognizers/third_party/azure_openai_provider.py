import logging
import os
from typing import Optional

try:
    import langextract as lx
    import openai
    from langextract.providers.openai import OpenAILanguageModel
    LANGEXTRACT_OPENAI_AVAILABLE = True
except ImportError:
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
except ImportError:
    AZURE_IDENTITY_AVAILABLE = False
    ChainedTokenCredential = None
    DefaultAzureCredential = None
    EnvironmentCredential = None
    ManagedIdentityCredential = None
    WorkloadIdentityCredential = None
    get_bearer_token_provider = None

logger = logging.getLogger("presidio-analyzer")


# Only define the class if dependencies are available
# This prevents "TypeError: NoneType takes no arguments" when langextract
# is not installed
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

            if not api_key or azure_ad_token_provider:
                if not AZURE_IDENTITY_AVAILABLE and not azure_ad_token_provider:
                    raise ImportError(
                        "azure-identity is required for managed identity "
                        "authentication. Install it with: pip install azure-identity"
                    )

                if azure_ad_token_provider:
                    token_provider = azure_ad_token_provider
                else:
                    if os.getenv('ENV') == 'development':
                        credential = DefaultAzureCredential()
                    else:
                        credential = ChainedTokenCredential(
                            EnvironmentCredential(),
                            WorkloadIdentityCredential(),
                            ManagedIdentityCredential()
                        )

                    token_provider = get_bearer_token_provider(
                        credential,
                        "https://cognitiveservices.azure.com/.default"
                    )

                self._client = openai.AzureOpenAI(
                    azure_ad_token_provider=token_provider,
                    azure_endpoint=self.azure_endpoint,
                    api_version=self.api_version
                )

                logger.info(
                    f"Initialized Azure OpenAI provider with managed identity: "
                    f"endpoint={self.azure_endpoint}, "
                    f"deployment={self.azure_deployment}"
                )
            else:
                self._client = openai.AzureOpenAI(
                    api_key=self.api_key,
                    azure_endpoint=self.azure_endpoint,
                    api_version=self.api_version
                )

                logger.info(
                    f"Initialized Azure OpenAI provider with API key: "
                    f"endpoint={self.azure_endpoint}, "
                    f"deployment={self.azure_deployment}, "
                    f"api_version={self.api_version}"
                )

        def _get_client_model_id(self) -> str:
            """
            Return the model/deployment identifier for API calls.

            For Azure OpenAI, this is the deployment name, not the base model name.

            :return: Azure deployment name.
            """
            return self.azure_deployment
else:
    class AzureOpenAILanguageModel:
        """Placeholder when langextract is not installed."""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "LangExtract with OpenAI support is not installed. "
                "Install it with: pip install presidio-analyzer[langextract,openai] "
                "or: pip install langextract[openai]"
            )


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
    except Exception as e:
        logger.warning(f"Failed to register Azure OpenAI provider: {e}")
