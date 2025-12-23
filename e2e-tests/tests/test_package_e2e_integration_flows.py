import pytest
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import EngineResult, OperatorResult

try:
    from presidio_analyzer.predefined_recognizers.third_party.\
        ollama_langextract_recognizer import OllamaLangExtractRecognizer
    OLLAMA_RECOGNIZER_AVAILABLE = True
except ImportError:
    OLLAMA_RECOGNIZER_AVAILABLE = False
    OllamaLangExtractRecognizer = None


@pytest.mark.package
def test_given_text_with_pii_using_package_then_analyze_and_anonymize_successfully():
    text_to_test = "John Smith drivers license is AC432223"

    expected_response = [
        RecognizerResult("PERSON", 0, 10, 0.85),
        RecognizerResult("US_DRIVER_LICENSE", 30, 38, 0.6499999999999999),
    ]
    # Create configuration containing engine name and models
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
    }

    # Create NLP engine based on configuration
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()

    # Pass the created NLP engine and supported_languages to the AnalyzerEngine
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
    analyzer_results = analyzer.analyze(text_to_test, "en")
    for i in range(len(analyzer_results)):
        assert analyzer_results[i] == expected_response[i]

    expected_response = EngineResult(
        text="<PERSON> drivers license is <US_DRIVER_LICENSE>"
    )
    expected_response.add_item(
        OperatorResult(
            operator="replace",
            entity_type="US_DRIVER_LICENSE",
            start=28,
            end=47,
            text="<US_DRIVER_LICENSE>",
        )
    )
    expected_response.add_item(
        OperatorResult(
            operator="replace",
            entity_type="PERSON",
            start=0,
            end=8,
            text="<PERSON>",
        )
    )

    anonymizer = AnonymizerEngine()
    anonymizer_results = anonymizer.anonymize(text_to_test, analyzer_results)
    assert anonymizer_results == expected_response


@pytest.mark.package
def test_given_text_with_pii_using_ollama_recognizer_then_detects_entities(tmp_path):
    """Test Ollama LangExtract recognizer detects entities when explicitly added to analyzer."""
    assert OLLAMA_RECOGNIZER_AVAILABLE, "LangExtract must be installed for e2e tests"

    text_to_test = "Patient John Smith, SSN 123-45-6789, email john@example.com, phone 555-123-4567, lives at 123 Main St, works at Acme Corp"

    # Use pre-configured config file with small model (qwen2.5:1.5b)
    import os
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "resources", "ollama_test_config.yaml"
    )

    # Create Ollama recognizer with custom config and custom name
    ollama_recognizer = OllamaLangExtractRecognizer(
        config_path=config_path, name="e2eollama"
    )

    # Verify the recognizer has the custom name
    assert ollama_recognizer.name == "e2eollama", \
        f"Expected recognizer name to be 'e2eollama', got '{ollama_recognizer.name}'"

    # Create analyzer with ONLY Ollama recognizer (no NLP engine, no default recognizers)
    from presidio_analyzer.recognizer_registry import RecognizerRegistry
    registry = RecognizerRegistry()
    registry.add_recognizer(ollama_recognizer)
    
    analyzer = AnalyzerEngine(
        registry=registry,
        supported_languages=["en"]
    )

    # Analyze text
    results = analyzer.analyze(text_to_test, language="en")

    # Verify at least some entities were detected
    assert len(results) > 0, "Expected to detect at least one PII entity"

    # Check which recognizers participated in detection
    recognizers_used = set()
    langextract_detected_at_least_one = False
    
    for result in results:
        if result.recognition_metadata:
            recognizer_name = result.recognition_metadata.get(
                RecognizerResult.RECOGNIZER_NAME_KEY, ""
            )
            recognizers_used.add(recognizer_name)
            
            langextract_detected_at_least_one |= (
                recognizer_name == "e2eollama"
            )
    
    # Verify that Ollama LangExtract recognizer participated in detection
    assert langextract_detected_at_least_one, \
        f"Expected 'e2eollama' recognizer to detect at least one entity. Recognizers used: {recognizers_used}"


@pytest.mark.package
def test_ollama_recognizer_loads_from_yaml_configuration_when_enabled():
    """
    E2E test to verify Ollama recognizer can be enabled via YAML configuration.
    
    The test ensures that when enabled=true in the YAML config:
    1. The recognizer loads successfully (handles supported_language and context kwargs)
    2. The config_path is resolved correctly (handles relative paths)
    3. The recognizer can detect PII entities
    
    Prerequisites:
    - Ollama service running with qwen2.5:1.5b model
    - LangExtract library installed
    """
    if not OLLAMA_RECOGNIZER_AVAILABLE:
        pytest.skip("LangExtract not installed")
    
    # Check if Ollama is available
    import os
    try:
        import requests
        ollama_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        if response.status_code != 200:
            pytest.skip("Ollama service not available")
    except Exception:
        pytest.skip("Ollama service not available")
    
    # Load recognizer registry from YAML config with Ollama enabled
    from presidio_analyzer.recognizer_registry import RecognizerRegistryProvider
    
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "resources", "test_ollama_enabled_recognizers.yaml"
    )
    
    
    provider = RecognizerRegistryProvider(conf_file=config_path)
    registry = provider.create_recognizer_registry()
    
    # Verify Ollama recognizer was loaded from config with custom name (direct match)
    ollama_recognizer = registry.get_recognizer("e2eollama")
    assert ollama_recognizer is not None, \
        "Expected to find recognizer with name 'e2eollama' in registry"
    
    # Verify the recognizer is actually an instance of the correct class
    assert ollama_recognizer.__class__.__name__ == "OllamaLangExtractRecognizer", \
        f"Expected class OllamaLangExtractRecognizer, got {ollama_recognizer.__class__.__name__}"
    
    # Verify language and entities
    assert ollama_recognizer.supported_language == "en"
    assert len(ollama_recognizer.supported_entities) > 0
    
    # Test functionality: analyze text with the loaded recognizer
    analyzer = AnalyzerEngine(registry=registry, supported_languages=["en"])
    
    text_to_test = "Patient John Smith, SSN 123-45-6789, email john@example.com, phone 555-123-4567, lives at 123 Main St, works at Acme Corp"
    results = analyzer.analyze(text_to_test, language="en")
    
    # Should detect entities
    assert len(results) > 0, "Expected to detect at least one PII entity"
    
    # At minimum, other recognizers should detect common entities
    entity_types = {r.entity_type for r in results}
    expected_entities = {"EMAIL_ADDRESS", "PERSON", "PHONE_NUMBER", "US_SSN"}
    detected_expected = entity_types & expected_entities
    
    assert len(detected_expected) >= 2, \
        f"Expected at least 2 entities from {expected_entities}, detected: {entity_types}"
    
    print(f"\n✓ Ollama recognizer 'e2eollama' loaded successfully from YAML config")
    print(f"  Class: {ollama_recognizer.__class__.__name__}")
    print(f"  Detected entities: {entity_types}")
