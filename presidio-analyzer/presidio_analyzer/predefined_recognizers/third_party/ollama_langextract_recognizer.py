import logging
import urllib.error
import urllib.request
from pathlib import Path
from typing import List, Optional

try:
    import langextract as lx
    LANGEXTRACT_AVAILABLE = True
except ImportError:
    LANGEXTRACT_AVAILABLE = False
    lx = None

from presidio_analyzer.predefined_recognizers.third_party.\
    langextract_recognizer import LangExtractRecognizer

logger = logging.getLogger("presidio-analyzer")

OLLAMA_INSTALL_DOCS = "https://github.com/google/langextract#using-local-llms-with-ollama"

class OllamaLangExtractRecognizer(LangExtractRecognizer):
    """LangExtract recognizer using Ollama backend."""

    DEFAULT_CONFIG_PATH = (
        Path(__file__).parent.parent.parent / "conf" / "langextract_config_ollama.yaml"
    )

    def __init__(self, config_path: Optional[str] = None):
        """Initialize Ollama LangExtract recognizer."""
        # Determine actual config path
        actual_config_path = (
            config_path if config_path else str(self.DEFAULT_CONFIG_PATH)
        )

        super().__init__(
            config_path=actual_config_path,
            name="Ollama LangExtract PII"
        )

        model_config = self.config.get("model", {})
        self.model_url = model_config.get("model_url")
        if not self.model_url:
            raise ValueError("Ollama model configuration must contain 'model_url'")

        self._validate_ollama_setup()

    def _validate_ollama_setup(self) -> None:
        """Validate Ollama server and model availability."""
        if not self._check_ollama_server():
            error_msg = (
                f"Ollama server not reachable at {self.model_url}. "
                f"Please ensure Ollama is running. "
                f"Installation guide: {OLLAMA_INSTALL_DOCS}"
            )
            logger.error(error_msg)
            raise ConnectionError(error_msg)

        if not self._check_model_available():
            error_msg = (
                f"Model '{self.model_id}' not found. "
                f"Please install it manually by running:\n"
                f"  ollama pull {self.model_id}\n"
                f"Installation guide: {OLLAMA_INSTALL_DOCS}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        logger.info(f"Ollama LangExtract initialized with model '{self.model_id}'")

    def _check_ollama_server(self) -> bool:
        """Check if Ollama server is running and accessible."""
        try:
            url = f"{self.model_url}/api/tags"
            request = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status == 200
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            logger.warning(f"Ollama server check failed at {self.model_url}: {e}")
            return False

    def _check_model_available(self) -> bool:
        """Check if the configured model is pulled and available."""
        try:
            url = f"{self.model_url}/api/tags"
            request = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(request, timeout=5) as response:
                import json
                data = json.loads(response.read().decode('utf-8'))
                models = data.get('models', [])

                for model in models:
                    model_name = model.get('name', '')
                    if model_name.startswith(self.model_id):
                        return True
                return False
        except Exception as e:
            logger.warning(f"Model availability check failed: {e}")
            return False

    def _call_langextract(
        self,
        text: str,
        prompt: str,
        examples: List,
        **kwargs
    ):
        """Call Ollama through LangExtract."""
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
