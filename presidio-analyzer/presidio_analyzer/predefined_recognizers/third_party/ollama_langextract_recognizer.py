import logging
from pathlib import Path
from typing import List, Optional

from presidio_analyzer.llm_utils import get_langextract_module
from presidio_analyzer.predefined_recognizers.third_party.\
    langextract_recognizer import LangExtractRecognizer

logger = logging.getLogger("presidio-analyzer")

class OllamaLangExtractRecognizer(LangExtractRecognizer):
    """LangExtract recognizer using Ollama backend."""

    DEFAULT_CONFIG_PATH = (
        Path(__file__).parent.parent.parent / "conf" / "langextract_config_ollama.yaml"
    )

    def __init__(self, config_path: Optional[str] = None):
        """Initialize Ollama LangExtract recognizer.

        Note: Ollama server availability and model availability are not validated
        during initialization. Any connectivity or model issues will be reported
        when analyze() is first called.
        """
        # Determine actual config path
        actual_config_path = (
            config_path if config_path else str(self.DEFAULT_CONFIG_PATH)
        )

        try:
            super().__init__(
                config_path=actual_config_path,
                name="Ollama LangExtract PII"
            )

            model_config = self.config.get("model", {})
            self.model_url = model_config.get("model_url")
            if not self.model_url:
                raise ValueError("Ollama model configuration must contain 'model_url'")
        except Exception:
            logger.exception(
                "Failed to initialize Ollama LangExtract recognizer. "
                "Check that configuration file exists and is valid, and that "
                "required dependencies (langextract, Jinja2) are installed."
            )
            raise

    def _call_langextract(
        self,
        text: str,
        prompt: str,
        examples: List,
        **kwargs
    ):
        """Call Ollama through LangExtract.

        This method will raise exceptions if:
        - Ollama server is not running or unreachable
        - Requested model is not installed in Ollama
        - Network errors occur during extraction

        Errors are logged with full traceback for debugging.
        """
        lx = get_langextract_module()

        try:
            extract_params = {
                "text_or_documents": text,
                "prompt_description": prompt,
                "examples": examples,
                "model_id": self.model_id,
                "model_url": self.model_url,
            }

            if self.temperature is not None:
                extract_params["temperature"] = self.temperature

            extract_params.update(kwargs)

            return lx.extract(**extract_params)
        except Exception:
            logger.exception(
                "LangExtract extraction failed. Common causes: "
                "Ollama server not running at %s, "
                "model '%s' not installed (run 'ollama pull %s'), "
                "or network connectivity issues.",
                self.model_url,
                self.model_id,
                self.model_id
            )
            raise
