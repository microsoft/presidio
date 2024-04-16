import re
from pathlib import Path

from presidio_analyzer import AnalyzerEngineProvider
from presidio_analyzer.nlp_engine import SpacyNlpEngine

from presidio_analyzer.nlp_engine.transformers_nlp_engine import TransformersNlpEngine


def test_analyzer_engine_provider_default_configuration(mandatory_recognizers):
    provider = AnalyzerEngineProvider()
    engine = provider.create_engine()
    assert engine.supported_languages == ["en"]
    assert engine.registry.global_regex_flags == re.DOTALL | re.MULTILINE | re.IGNORECASE
    assert engine.default_score_threshold == 0
    names = [recognizer.name for recognizer in engine.registry.recognizers]
    for predefined_recognizer in mandatory_recognizers:
        assert predefined_recognizer in names
    assert "SpacyRecognizer" in names
    assert isinstance(engine.nlp_engine, SpacyNlpEngine)
    assert engine.nlp_engine.engine_name == "spacy"


def test_analyzer_engine_provider_configuration_file():
    this_path = Path(__file__).parent.absolute()
    test_yaml = Path(this_path, "conf/test_analyzer_engine.yaml")
    provider = AnalyzerEngineProvider(test_yaml)
    engine = provider.create_engine()
    assert engine.supported_languages == ["en", "es"]
    assert engine.default_score_threshold == 0.7
    recognizer_registry = engine.registry
    assert recognizer_registry.global_regex_flags == re.DOTALL | re.MULTILINE | re.IGNORECASE
    assert len(recognizer_registry.recognizers) == 9
    assert [recognizer.supported_language for recognizer in recognizer_registry.recognizers if recognizer.name == "ItFiscalCodeRecognizer"] == ["en", "es"]
    assert [recognizer.supported_language for recognizer in recognizer_registry.recognizers if recognizer.name == "CreditCardRecognizer"] == ["en"]
    assert [recognizer.supported_language for recognizer in recognizer_registry.recognizers if recognizer.name == "ZipCodeRecognizer"] == ["de"]
    assert [recognizer.supported_language for recognizer in recognizer_registry.recognizers if recognizer.name == "ExampleCustomRecognizer"] == ["en", "es"]
    assert sorted([recognizer.supported_language for recognizer in recognizer_registry.recognizers if recognizer.name == "TransformersRecognizer"]) == sorted(["en", "de", "es"])
    spanish_recognizer = [recognizer for recognizer in recognizer_registry.recognizers if recognizer.name == "ExampleCustomRecognizer" and recognizer.supported_language == "es"][0]
    assert spanish_recognizer.context == ["tarjeta", "credito"]
    assert isinstance(engine.nlp_engine, TransformersNlpEngine)
    assert engine.nlp_engine.engine_name == "transformers"


def test_analyzer_engine_provider_configuration_file_missing_values_expect_defaults(mandatory_recognizers):
    this_path = Path(__file__).parent.absolute()
    test_yaml = Path(this_path, "conf/test_analyzer_engine_missing_values.yaml")
    provider = AnalyzerEngineProvider(test_yaml)
    engine = provider.create_engine()
    assert engine.supported_languages == ["de"]
    assert engine.default_score_threshold == 0
    recognizer_registry = engine.registry
    assert recognizer_registry.global_regex_flags == re.DOTALL | re.MULTILINE | re.IGNORECASE
    assert recognizer_registry.supported_languages == ["de"]
    names = [recognizer.name for recognizer in recognizer_registry.recognizers]
    for predefined_recognizer in mandatory_recognizers:
        assert predefined_recognizer in names
    assert isinstance(engine.nlp_engine, SpacyNlpEngine)
    assert engine.nlp_engine.engine_name == "spacy"