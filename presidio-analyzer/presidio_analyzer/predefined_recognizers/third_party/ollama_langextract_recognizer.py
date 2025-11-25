import logging
from pathlib import Path
from typing import Optional

from presidio_analyzer.llm_utils import check_langextract_available, lx
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
    ):
        """Initialize Ollama LangExtract recognizer.

        Note: Ollama server availability and model availability are not validated
        during initialization. Any connectivity or model issues will be reported
        when analyze() is first called.
        
        :param config_path: Path to configuration file (optional).
        :param supported_language: Language this recognizer supports (optional, default: "en").
        :param context: List of context words (optional, currently not used by LLM recognizers).
        """
        # Determine actual config path
        if config_path:
            config_path_obj = Path(config_path)
            # If path is not absolute and doesn't exist as-is, resolve relative to package root
            if not config_path_obj.is_absolute() and not config_path_obj.exists():
                # Try to resolve relative to presidio-analyzer package root
                # From this file: presidio-analyzer/presidio_analyzer/predefined_recognizers/third_party/
                # Go up to: presidio-analyzer/
                package_root = Path(__file__).parent.parent.parent.parent
                resolved_path = package_root / config_path
                if resolved_path.exists():
                    actual_config_path = str(resolved_path)
                else:
                    # If not found, try as-is (will likely fail but with clear error)
                    actual_config_path = config_path
            else:
                actual_config_path = str(config_path_obj)
        else:
            actual_config_path = str(self.DEFAULT_CONFIG_PATH)

        try:
            super().__init__(
                config_path=actual_config_path,
                name="Ollama LangExtract PII"
            )

            model_config = self.config.get("model", {})
            self.model_url = model_config.get("model_url")
            if not self.model_url:
                raise ValueError("Ollama model configuration must contain 'model_url'")
        except Exception as e:
            logger.exception("Failed to initialize Ollama recognizer: %s", str(e))
            raise

    def _call_langextract(self, **kwargs):
        """Call Ollama through LangExtract."""
        check_langextract_available()

        try:
            # Add Ollama-specific parameters
            extract_params = {
                "text_or_documents": kwargs.pop("text"),
                "prompt_description": kwargs.pop("prompt"),
                "examples": kwargs.pop("examples"),
                "model_id": self.model_id,
                "model_url": self.model_url,
            }

            # Pass through temperature and any other kwargs
            extract_params.update(kwargs)

            return lx.extract(**extract_params)
        except Exception as e:
            logger.exception(
                "LangExtract extraction failed (Ollama at %s, model '%s'): %s",
                self.model_url, self.model_id, str(e)
            )
            raise
