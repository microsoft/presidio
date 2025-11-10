import logging
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

try:
    import langextract as lx
    LANGEXTRACT_AVAILABLE = True
except ImportError:
    LANGEXTRACT_AVAILABLE = False
    lx = None

from presidio_analyzer.predefined_recognizers.third_party.langextract_recognizer import LangExtractRecognizer

logger = logging.getLogger("presidio-analyzer")

OLLAMA_INSTALL_DOCS = "https://github.com/google/langextract#using-local-llms-with-ollama"

class OllamaLangExtractRecognizer(LangExtractRecognizer):
    """
    Concrete implementation of LangExtract recognizer using Ollama backend.
    
    Provides Ollama-specific functionality including:
    - Ollama server connectivity validation
    - Model availability checks
    - Ollama API integration with LangExtract
    """

    DEFAULT_CONFIG_PATH = (
        Path(__file__).parent.parent.parent / "conf" / "ollama_config.yaml"
    )

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        supported_language: str = "en",
        config_path: Optional[str] = None,
        name: str = "Ollama LangExtract PII/PHI",
        version: str = "1.0.0",
        **kwargs
    ):
        """
        Initialize Ollama LangExtract recognizer for PII/PHI detection.

        :param supported_entities: List of PII/PHI entities to detect.
        :param supported_language: Language code (only 'en' supported).
        :param config_path: Path to YAML configuration file.
        :param name: Recognizer name.
        :param version: Recognizer version.
        :param kwargs: Additional arguments for parent class.
        """
        # Load Ollama-specific configuration first
        ollama_config = self._load_ollama_config(config_path)
        
        # Extract Ollama-specific parameters
        model_id = ollama_config.get("model_id")
        if not model_id:
            raise ValueError("Ollama configuration must contain 'model_id'")
            
        self.model_url = ollama_config.get("model_url")
        if not self.model_url:
            raise ValueError("Ollama configuration must contain 'model_url'")
        
        temperature = ollama_config.get("temperature")
        
        # Initialize parent with Ollama-specific parameters
        super().__init__(
            supported_entities=supported_entities,
            supported_language=supported_language,
            config_path=config_path,
            name=name,
            version=version,
            model_id=model_id,
            temperature=temperature,
            min_score=None,  # Will be loaded from langextract config
            **kwargs
        )
        
        # Validate Ollama setup during initialization
        self._validate_ollama_setup()

    def _load_ollama_config(self, config_path: Optional[str] = None) -> Dict:
        """Load Ollama-specific configuration.
        
        :param config_path: Path to configuration file.
        :return: Ollama configuration dictionary.
        """
        if config_path is None:
            config_path = self.DEFAULT_CONFIG_PATH
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}"
            )

        import yaml
        with open(config_path, 'r') as f:
            full_config = yaml.safe_load(f)

        ollama_config = full_config.get("ollama", {})

        if not ollama_config:
            raise ValueError(
                "Configuration file must contain 'ollama' section with Ollama-specific config"
            )

        return ollama_config

    def _validate_ollama_setup(self) -> None:
        """Validate Ollama server and model availability."""
        if not self._validate_llm_availability():
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

    def _validate_llm_availability(self) -> bool:
        """Check if Ollama server is running and accessible."""
        return self._check_ollama_server()

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

                # Check if our model is in the list
                for model in models:
                    model_name = model.get('name', '')
                    # Match both "gemma3:1b" and "gemma3:1b:latest"
                    if model_name.startswith(self.model_id):
                        return True
                return False
        except Exception as e:
            logger.warning(f"Model availability check failed: {e}")
            return False

    def _call_llm(
        self,
        text: str,
        prompt: str,
        examples: List,
        **kwargs
    ):
        """
        Call Ollama through LangExtract for PII extraction.
        
        :param text: Text to analyze.
        :param prompt: Prompt description for LangExtract.
        :param examples: LangExtract examples.
        :param kwargs: Additional parameters.
        :return: LangExtract result object.
        """
        extract_params = {
            "text_or_documents": text,
            "prompt_description": prompt,
            "examples": examples,
            "model_id": self.model_id,
        }

        # Ollama-specific parameters
        extract_params["model_url"] = self.model_url
        if self.temperature is not None:
            extract_params["temperature"] = self.temperature

        # Add any additional kwargs
        extract_params.update(kwargs)

        return lx.extract(**extract_params)
