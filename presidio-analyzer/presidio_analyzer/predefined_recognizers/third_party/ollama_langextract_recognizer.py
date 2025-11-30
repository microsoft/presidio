import logging
from pathlib import Path
from typing import Optional

from presidio_analyzer.llm_utils import lx
from presidio_analyzer.predefined_recognizers.third_party.\
    langextract_recognizer import LangExtractRecognizer

logger = logging.getLogger("presidio-analyzer")

class OllamaLangExtractRecognizer(LangExtractRecognizer):
    """LangExtract recognizer using Ollama backend."""

    DEFAULT_CONFIG_PATH = (
        Path(__file__).parent.parent.parent / "conf" / "langextract_config_ollama.yaml"
    )

    def __init__(
        self,
        config_path: Optional[str] = None,
        supported_language: str = "en",
        context: Optional[list] = None,
        **kwargs,
    ):
        """Initialize Ollama LangExtract recognizer.

        Note: Ollama server availability and model availability are not validated
        during initialization. Any connectivity or model issues will be reported
        when analyze() is first called.

        :param config_path: Path to configuration file (optional).
        :param supported_language: Language this recognizer supports
            (optional, default: "en").
        :param context: List of context words
            (optional, currently not used by LLM recognizers).
        :param kwargs: Additional keyword arguments (unused, allows flexibility
            when instantiated from YAML configuration).
        """
        actual_config_path = (
            config_path if config_path else str(self.DEFAULT_CONFIG_PATH)
        )

        super().__init__(
            config_path=actual_config_path,
            name="Ollama LangExtract PII",
            supported_language=supported_language
        )

        model_config = self.config.get("model", {})
        self.model_url = model_config.get("model_url")
        if not self.model_url:
            raise ValueError("Ollama model configuration must contain 'model_url'")

    def _call_langextract(self, **kwargs):
        """Call Ollama through LangExtract."""
        try:
            extract_params = {
                "text_or_documents": kwargs.pop("text"),
                "prompt_description": kwargs.pop("prompt"),
                "examples": kwargs.pop("examples"),
                "model_id": self.model_id,
                "model_url": self.model_url,
            }

            extract_params.update(kwargs)

            return lx.extract(**extract_params)
        except Exception:
            logger.exception(
                "LangExtract extraction failed (Ollama at %s, model '%s')",
                self.model_url, self.model_id
            )
            raise
