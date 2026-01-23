import logging
import os
from pathlib import Path
from typing import Any, Optional

from presidio_analyzer.llm_utils import lx_factory
from presidio_analyzer.predefined_recognizers.third_party.\
    langextract_recognizer import LangExtractRecognizer

logger = logging.getLogger("presidio-analyzer")

class BasicLangExtractRecognizer(LangExtractRecognizer):
    """Basic LangExtract recognizer using configurable backend."""

    DEFAULT_CONFIG_PATH = (
        Path(__file__).parent.parent.parent / "conf" / "langextract_config_basic.yaml"
    )

    def __init__(
        self,
        config_path: Optional[str] = None,
        supported_language: str = "en",
        context: Optional[list] = None
    ):
        """Initialize Basic LangExtract recognizer.

        :param config_path: Path to configuration file (optional).
        :param supported_language: Language this recognizer supports
            (optional, default: "en").
        :param context: List of context words
            (optional, currently not used by LLM recognizers).
        """
        actual_config_path = (
            config_path if config_path else str(self.DEFAULT_CONFIG_PATH)
        )

        model_config = self.config.get("model", {})
        extract_params: dict[str, dict[str, Any]] = {}
        if "max_char_buffer" in model_config:
            extract_params["extract"] = {
                "max_char_buffer": model_config["max_char_buffer"]
            }

        for key in ["timeout", "num_ctx"]:
            if key in model_config:
                extract_params["language_model"][key] = model_config[key]

        super().__init__(
            config_path=actual_config_path,
            name="Basic LangExtract PII",
            supported_language=supported_language,
            extract_params=extract_params,
        )

        provider_config = model_config.get("provider", {})
        self.model_id = model_config.get("model_id")
        self.provider = provider_config.get("name")
        self.provider_kwargs = provider_config.get("kwargs", {})
        if not self.model_id:
            raise ValueError("Configuration must contain 'model_id'")
        if not self.provider:
            raise ValueError("Configuration must contain 'provider'")

        self.fence_output = model_config.get("fence_output", "openai" in self.provider.lower())
        self.use_schema_constraints = model_config.get("use_schema_constraints", False)

        if "api_key" not in self.provider_kwargs and "LANGEXTRACT_API_KEY" in os.environ:
            self.provider_kwargs["api_key"] = os.environ["LANGEXTRACT_API_KEY"]

        self.lx_model_config = lx_factory.ModelConfig(
            model_id=self.model_id,
            provider=self.provider,
            provider_kwargs=self.provider_kwargs,
        )

    def _get_provider_params(self):
        """Return Azure OpenAI-specific params."""
        return {
            "config": self.lx_model_config,
            "fence_output": self.fence_output,
            "use_schema_constraints": self.use_schema_constraints,
        }
