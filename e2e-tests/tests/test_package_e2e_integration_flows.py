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
@pytest.mark.timeout(360)  # 6 minutes timeout for slow CI runners
def test_given_text_with_pii_using_ollama_recognizer_then_detects_entities():
    """Test Ollama LangExtract recognizer detects PII entities when explicitly added to analyzer."""
    assert OLLAMA_RECOGNIZER_AVAILABLE, "LangExtract must be installed for e2e tests"

    text_to_test = "John Smith works at Microsoft and his email is john@microsoft.com"

    # Create NLP engine configuration
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
    }
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()

    # Create Ollama recognizer explicitly
    ollama_recognizer = OllamaLangExtractRecognizer()

    # Create analyzer and add Ollama recognizer
    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=["en"]
    )
    analyzer.registry.add_recognizer(ollama_recognizer)

    # Analyze text with return_decision_process to inspect recognizers
    results = analyzer.analyze(text_to_test, language="en", return_decision_process=True)

    # Verify results
    assert len(results) > 0, "Expected to detect PII entities"

    # Check that at least PERSON entity is detected
    entity_types = [result.entity_type for result in results]
    assert "PERSON" in entity_types, "Expected to detect PERSON entity"

    # Verify that Ollama recognizer participated in detection
    recognizers_used = {result.analysis_explanation.recognizer for result in results}
    ollama_recognizer_names = [name for name in recognizers_used if "ollama" in name.lower() or "langextract" in name.lower()]
    assert len(ollama_recognizer_names) > 0, "Ollama recognizer should have detected at least one entity"

    # Anonymize the detected entities
    anonymizer = AnonymizerEngine()
    anonymized_result = anonymizer.anonymize(text_to_test, results)

    # Verify anonymization occurred
    assert anonymized_result.text != text_to_test, "Text should be anonymized"
    assert "<PERSON>" in anonymized_result.text or "John Smith" not in anonymized_result.text


@pytest.mark.package
def test_given_ollama_server_not_running_then_raises_connection_error(tmp_path):
    """Test that initializing Ollama recognizer when server is not running raises ConnectionError."""
    assert OLLAMA_RECOGNIZER_AVAILABLE, "LangExtract must be installed for e2e tests"

    import yaml

    config = {
        "langextract": {
            "supported_entities": ["PERSON", "EMAIL_ADDRESS"],
            "entity_mappings": {"person": "PERSON", "email": "EMAIL_ADDRESS"},
            "prompt_file": "langextract_prompts/default_pii_phi_prompt.txt",
            "examples_file": "langextract_prompts/default_pii_phi_examples.yaml",
            "min_score": 0.5,
        },
        "ollama": {
            "model_id": "gemma2:2b",
            "model_url": "http://localhost:9999",
            "temperature": 0.0,
        }
    }

    config_file = tmp_path / "test_config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config, f)

    with pytest.raises(ConnectionError, match="Ollama server not reachable"):
        OllamaLangExtractRecognizer(config_path=str(config_file))


@pytest.mark.package
def test_given_model_not_pulled_then_raises_runtime_error(tmp_path):
    """Test that initializing Ollama recognizer with unpulled model raises RuntimeError."""
    assert OLLAMA_RECOGNIZER_AVAILABLE, "LangExtract must be installed for e2e tests"

    import yaml

    config = {
        "langextract": {
            "supported_entities": ["PERSON", "EMAIL_ADDRESS"],
            "entity_mappings": {"person": "PERSON", "email": "EMAIL_ADDRESS"},
            "prompt_file": "langextract_prompts/default_pii_phi_prompt.txt",
            "examples_file": "langextract_prompts/default_pii_phi_examples.yaml",
            "min_score": 0.5,
        },
        "ollama": {
            "model_id": "llama3.2:1b",
            "model_url": "http://localhost:11434",
            "temperature": 0.0,
        }
    }

    config_file = tmp_path / "test_config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config, f)

    with pytest.raises(RuntimeError, match="Model .* not found"):
        OllamaLangExtractRecognizer(config_path=str(config_file))


@pytest.mark.package
def test_given_nonexistent_model_then_raises_runtime_error(tmp_path):
    """Test that initializing Ollama recognizer with non-existent model raises RuntimeError."""
    assert OLLAMA_RECOGNIZER_AVAILABLE, "LangExtract must be installed for e2e tests"

    import yaml

    config = {
        "langextract": {
            "supported_entities": ["PERSON", "EMAIL_ADDRESS"],
            "entity_mappings": {"person": "PERSON", "email": "EMAIL_ADDRESS"},
            "prompt_file": "langextract_prompts/default_pii_phi_prompt.txt",
            "examples_file": "langextract_prompts/default_pii_phi_examples.yaml",
            "min_score": 0.5,
        },
        "ollama": {
            "model_id": "nonexistent-fake-model-xyz-12345",
            "model_url": "http://localhost:11434",
            "temperature": 0.0,
        }
    }

    config_file = tmp_path / "test_config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config, f)

    with pytest.raises(RuntimeError, match="Model .* not found"):
        OllamaLangExtractRecognizer(config_path=str(config_file))


@pytest.mark.package
def test_given_text_with_ollama_recognizer_and_score_threshold_then_filters_results():
    """Test Ollama recognizer with score threshold filtering."""
    assert OLLAMA_RECOGNIZER_AVAILABLE, "LangExtract must be installed for e2e tests"

    text_to_test = "Contact Alice at alice@example.com or call 555-1234"

    ollama_recognizer = OllamaLangExtractRecognizer()

    analyzer = AnalyzerEngine(
        supported_languages=["en"],
        registry=None
    )
    analyzer.registry.add_recognizer(ollama_recognizer)

    results_high_threshold = analyzer.analyze(
        text_to_test,
        language="en",
        score_threshold=0.8
    )

    results_low_threshold = analyzer.analyze(
        text_to_test,
        language="en",
        score_threshold=0.3
    )

    assert len(results_low_threshold) >= len(results_high_threshold), \
        "Low threshold should return at least as many results as high threshold"

    for result in results_high_threshold:
        assert result.score >= 0.8, f"Result score {result.score} should be >= 0.8"

    for result in results_low_threshold:
        assert result.score >= 0.3, f"Result score {result.score} should be >= 0.3"


