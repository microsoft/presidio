import logging
from pathlib import Path
from typing import Any, Dict, Optional

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
        name: str = "Ollama LangExtract PII",
    ):
        """Initialize Ollama LangExtract recognizer."""
        actual_config_path = (
            config_path if config_path else str(self.DEFAULT_CONFIG_PATH)
        )

        super().__init__(
            config_path=actual_config_path,
            name=name,
            supported_language=supported_language,
            extract_params={
                "extract": {
                    "use_schema_constraints": False,
                    "fence_output": False,
                    "max_char_buffer": 400,
                },
                "language_model": {
                    "timeout": 240,
                    "num_ctx": 8192,
                }
            },
        )

        model_config = self.config.get("model", {})
        self.model_url = model_config.get("model_url")
        if not self.model_url:
            raise ValueError("Ollama model configuration must contain 'model_url'")

    def _get_provider_params(self) -> Dict[str, Any]:
        """Return Ollama-specific params."""
        return {
            "model_id": self.model_id,
            "model_url": self.model_url,
        }
