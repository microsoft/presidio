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


def _setup_ollama_for_tests():
    """Run install_ollama_model.py script to setup Ollama."""
    script_path = Path(__file__).parent.parent / "install_ollama_model.py"
    if not script_path.exists():
        print(f"⚠ Ollama setup script not found: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            ["python", str(script_path)],
            capture_output=True,
            timeout=600,  # 10 minutes for installation + startup
            text=True
        )
        if result.returncode == 0:
            print("✓ Ollama setup completed via install_ollama_model.py")
            return True
        else:
            print(f"✗ Ollama setup failed: {result.stderr}")
            return False
    except subprocess.SubprocessError as e:
        print(f"✗ Failed to run Ollama setup script: {e}")
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
    Check if Ollama is running and ready for LangExtract tests.
    Attempts to auto-install and setup if not found.
    """
    if not REQUESTS_AVAILABLE:
        print("⚠ requests library not available - skipping Ollama tests")
        return False
    
    # First check if Ollama is already ready
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✓ Ollama already running and ready")
            return True
    except Exception:
        # Ollama not available, will attempt setup
        print("Ollama not responding, will attempt setup")
    
    # Not available - try to set up
    print("\n" + "="*60)
    print("Ollama not found - attempting automatic setup for tests")
    print("="*60)
    
    if not _setup_ollama_for_tests():
        print("⚠ Skipping LangExtract tests - Ollama setup failed")
        return False
    
    print("="*60)
    print("✓ Ollama ready for LangExtract tests!")
    print("="*60 + "\n")
    
    return True


@pytest.fixture(scope="session")
def nlp_recognizers() -> Dict[str, EntityRecognizer]:
    """Create NLP recognizer instances."""
    return {name: rec_cls() for name, rec_cls in NLP_RECOGNIZERS.items()}


@pytest.fixture(scope="session")
def langextract_recognizer_class(ollama_available, tmp_path_factory):
    """
    Provide LangExtractRecognizer class configured for testing.
    Creates a test config with enabled=true.
    Returns None if Ollama not available or langextract not installed.
    """
    if not ollama_available:
        return None
    
    try:
        from presidio_analyzer.predefined_recognizers import LangExtractRecognizer
        import yaml
        
        # Create a test-specific config with enabled=true
        config_dir = tmp_path_factory.mktemp("langextract_config")
        test_config_path = config_dir / "langextract_config.yaml"
        
        # Load default config and enable it for tests
        default_config_path = (
            Path(__file__).parent.parent / 
            "presidio_analyzer" / "conf" / "langextract_config.yaml"
        )
        
        with open(default_config_path) as f:
            config = yaml.safe_load(f)
        
        # Enable for tests
        config["langextract"]["enabled"] = True
        
        # Write test config
        with open(test_config_path, 'w') as f:
            yaml.dump(config, f)
        
        # Return a factory function that creates recognizers with the test config
        def create_recognizer(**kwargs):
            # Use test config if no config_path provided
            if 'config_path' not in kwargs:
                kwargs['config_path'] = str(test_config_path)
            return LangExtractRecognizer(**kwargs)
        
        # Store the class and config path for direct access
        create_recognizer.recognizer_class = LangExtractRecognizer
        create_recognizer.test_config_path = str(test_config_path)
        
        return create_recognizer
        
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
