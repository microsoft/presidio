import shutil
import subprocess
import platform
from pathlib import Path
from typing import Dict, List

import pytest

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from presidio_analyzer import (
    EntityRecognizer,
    Pattern,
    PatternRecognizer,
    AnalyzerEngine,
)
from presidio_analyzer import RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider, NlpEngine
from presidio_analyzer.predefined_recognizers import NLP_RECOGNIZERS, PREDEFINED_RECOGNIZERS
from tests.mocks import RecognizerRegistryMock, NlpEngineMock


def _install_ollama_for_tests():
    """Install Ollama if not already installed (for LangExtract tests)."""
    # Check if ollama command exists
    try:
        subprocess.run(["ollama", "--version"], 
                      capture_output=True, check=True, timeout=5)
        return True  # Already installed
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    
    print("\n=== Installing Ollama for LangExtract tests ===")
    
    system = platform.system()
    if system == "Linux":
        # Linux installation
        try:
            result = subprocess.run(
                ["curl", "-fsSL", "https://ollama.com/install.sh"],
                capture_output=True, check=True, timeout=30
            )
            subprocess.run(
                ["sh", "-c", result.stdout.decode()],
                check=True, timeout=300
            )
            print("✓ Ollama installed successfully")
            return True
        except subprocess.SubprocessError as e:
            print(f"✗ Failed to install Ollama: {e}")
            return False
    else:
        print(f"⚠ Automatic Ollama installation not supported on {system}")
        print("Please install manually from: https://ollama.com/download")
        return False


def _start_ollama_service():
    """Start Ollama service in background."""
    if not REQUESTS_AVAILABLE:
        return False
    
    try:
        # Check if already running
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            return True  # Already running
    except Exception:
        pass
    
    print("Starting Ollama service...")
    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Wait for service to start
        import time
        for _ in range(10):
            time.sleep(1)
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    print("✓ Ollama service started")
                    return True
            except Exception:
                continue
        print("✗ Ollama service did not start in time")
        return False
    except Exception as e:
        print(f"✗ Failed to start Ollama service: {e}")
        return False


def _pull_ollama_model(model_name="llama3.2:3b"):
    """Pull Ollama model if not already available."""
    if not REQUESTS_AVAILABLE:
        return False
    
    try:
        # Check if model already exists
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if any(model_name in m.get("name", "") for m in models):
                return True  # Already available
        
        print(f"\n=== Pulling Ollama model: {model_name} ===")
        print("This may take a few minutes (model is ~2GB)...")
        
        result = subprocess.run(
            ["ollama", "pull", model_name],
            check=True, timeout=600  # 10 minute timeout
        )
        print(f"✓ Model {model_name} pulled successfully")
        return True
    except subprocess.SubprocessError as e:
        print(f"✗ Failed to pull model: {e}")
        return False


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "skip_engine(nlp_engine): skip test for given nlp engine"
    )


@pytest.fixture(scope="session")
def nlp_engine_provider() -> NlpEngineProvider:
    return NlpEngineProvider()


@pytest.fixture(scope="session")
def nlp_engines(request, nlp_engine_provider) -> Dict[str, NlpEngine]:
    available_engines = {}

    nlp_engines = nlp_engine_provider.nlp_engines
    for name, engine_cls in nlp_engines.items():
        if name == "spacy":
            available_engines[f"{name}_en"] = engine_cls(
                models=[{"lang_code": "en", "model_name": "en_core_web_lg"}]
            )
        elif name == "stanza":
            available_engines[f"{name}_en"] = engine_cls(
                models=[{"lang_code": "en", "model_name": "en"}]
            )
        elif name == "transformers":
            available_engines[f"{name}_en"] = engine_cls(
                models=[
                    {
                        "lang_code": "en",
                        "model_name": {
                            "spacy": "en_core_web_sm",
                            "transformers": "StanfordAIMI/stanford-deidentifier-base",
                        },
                    }
                ]
            )
        else:
            raise ValueError("Unsupported engine for tests")

    return available_engines


@pytest.fixture(autouse=True)
def skip_by_engine(request, nlp_engines, ollama_available):
    marker = request.node.get_closest_marker("skip_engine")
    if marker:
        marker_arg = marker.args[0]
        # Check if it's an NLP engine
        if marker_arg in nlp_engines:
            return  # Engine is available
        # Special case for langextract (third-party recognizer, not NLP engine)
        if marker_arg == "langextract":
            if ollama_available:
                return  # Ollama is available
            pytest.skip(f"skipped - Ollama not available for langextract")
        else:
            pytest.skip(f"skipped on this engine: {marker_arg}")


@pytest.mark.skip_engine("spacy_en")
@pytest.fixture(scope="session")
def spacy_nlp_engine(nlp_engines):
    nlp_engine = nlp_engines.get("spacy_en", None)
    if nlp_engine:
        nlp_engine.load()
    return nlp_engine


@pytest.fixture(scope="session")
def ollama_available() -> bool:
    """
    Check if Ollama is running and llama3.2:3b model is available.
    Attempts to auto-install and setup if not found.
    """
    if not REQUESTS_AVAILABLE:
        return False
    
    # First check if already available
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if any("llama3.2:3b" in m.get("name", "") for m in models):
                return True  # Already set up
    except Exception:
        pass
    
    # Not available - try to set up
    print("\n" + "="*60)
    print("Ollama not found - attempting automatic setup for tests")
    print("="*60)
    
    # Step 1: Install Ollama
    if not _install_ollama_for_tests():
        print("⚠ Skipping LangExtract tests - Ollama installation failed")
        return False
    
    # Step 2: Start Ollama service
    if not _start_ollama_service():
        print("⚠ Skipping LangExtract tests - service failed to start")
        return False
    
    # Step 3: Pull model
    if not _pull_ollama_model("llama3.2:3b"):
        print("⚠ Skipping LangExtract tests - model pull failed")
        return False
    
    print("="*60)
    print("✓ Ollama setup complete for LangExtract tests!")
    print("="*60 + "\n")
    
    return True


@pytest.fixture(scope="session")
def nlp_recognizers() -> Dict[str, EntityRecognizer]:
    """Create NLP recognizer instances."""
    return {name: rec_cls() for name, rec_cls in NLP_RECOGNIZERS.items()}


@pytest.fixture(scope="session")
def langextract_recognizer_class(ollama_available):
    """
    Provide LangExtractRecognizer class if Ollama is available.
    Returns None if Ollama not available or langextract not installed.
    """
    if not ollama_available:
        return None
    
    try:
        from presidio_analyzer.predefined_recognizers import LangExtractRecognizer
        return LangExtractRecognizer
    except ImportError:
        return None


@pytest.fixture(scope="session")
def mandatory_recognizers() -> List[str]:
    return list(PREDEFINED_RECOGNIZERS)


@pytest.fixture(scope="session")
def ner_strength() -> float:
    return 0.85


@pytest.fixture(scope="session")
def max_score() -> float:
    return EntityRecognizer.MAX_SCORE


@pytest.fixture(scope="session")
def min_score() -> float:
    return EntityRecognizer.MIN_SCORE


@pytest.fixture(scope="module")
def loaded_registry() -> RecognizerRegistry:
    return RecognizerRegistry()


@pytest.fixture(scope="module")
def mock_registry() -> RecognizerRegistryMock:
    return RecognizerRegistryMock()


@pytest.fixture(scope="module")
def mock_nlp_engine() -> NlpEngineMock:
    return NlpEngineMock()


@pytest.fixture(scope="module")
def analyzer_engine_simple(mock_registry, mock_nlp_engine) -> AnalyzerEngine:
    return AnalyzerEngine(registry=mock_registry, nlp_engine=mock_nlp_engine)


@pytest.fixture(scope="session")
def zip_code_recognizer():
    regex = r"(\b\d{5}(?:\-\d{4})?\b)"
    zipcode_pattern = Pattern(name="zip code (weak)", regex=regex, score=0.01)
    zip_recognizer = PatternRecognizer(
        supported_entity="ZIP", patterns=[zipcode_pattern]
    )
    return zip_recognizer


def pytest_sessionfinish():
    """Remove files created during mock spaCy models creation."""

    mock_models = ("he_test", "bn_test")

    for mock_model in mock_models:
        test_model_path1 = Path(Path(__file__).parent, mock_model)
        test_model_path2 = Path(Path(__file__).parent.parent, mock_model)
        for path in (test_model_path1, test_model_path2):
            if path.exists():
                try:
                    shutil.rmtree(path)
                except OSError as e:
                    print("Failed to remove file: %s - %s." % (e.filename, e.strerror))
