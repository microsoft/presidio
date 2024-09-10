import re
from pathlib import Path

from presidio_analyzer import AnalyzerEngineProvider
from presidio_analyzer.nlp_engine import SpacyNlpEngine

from presidio_analyzer.nlp_engine.transformers_nlp_engine import TransformersNlpEngine

def get_full_paths(analyzer_yaml, nlp_engine_yaml=None, recognizer_registry_yaml=None):
    this_path = Path(__file__).parent.absolute()

    analyzer_yaml_path = Path(this_path, analyzer_yaml) if analyzer_yaml else None
    nlp_engine_yaml_path = Path(this_path, nlp_engine_yaml) if nlp_engine_yaml else None
    recognizer_registry_yaml_path = (
        Path(this_path, recognizer_registry_yaml) if recognizer_registry_yaml else None
    )
    return analyzer_yaml_path, nlp_engine_yaml_path, recognizer_registry_yaml_path


def test_analyzer_engine_provider_default_configuration(mandatory_recognizers):
    provider = AnalyzerEngineProvider()
    engine = provider.create_engine()
    assert engine.supported_languages == ["en"]
    assert (
        engine.registry.global_regex_flags == re.DOTALL | re.MULTILINE | re.IGNORECASE
    )
    assert engine.default_score_threshold == 0
    names = [recognizer.name for recognizer in engine.registry.recognizers]
    for predefined_recognizer in mandatory_recognizers:
        assert predefined_recognizer in names
    assert "SpacyRecognizer" in names
    assert isinstance(engine.nlp_engine, SpacyNlpEngine)
    assert engine.nlp_engine.engine_name == "spacy"


def test_analyzer_engine_provider_configuration_file():
    test_yaml, _, _ = get_full_paths("conf/test_analyzer_engine.yaml")
    provider = AnalyzerEngineProvider(test_yaml)
    engine = provider.create_engine()
    assert engine.supported_languages == ["de", "en", "es"]
    assert engine.default_score_threshold == 0.7
    recognizer_registry = engine.registry
    assert (
        recognizer_registry.global_regex_flags
        == re.DOTALL | re.MULTILINE | re.IGNORECASE
    )
    assert len(recognizer_registry.recognizers) == 8
    assert [
        recognizer.supported_language
        for recognizer in recognizer_registry.recognizers
        if recognizer.name == "ItFiscalCodeRecognizer"
    ] == ["de", "en", "es"]
    assert [
        recognizer.supported_language
        for recognizer in recognizer_registry.recognizers
        if recognizer.name == "CreditCardRecognizer"
    ] == ["en"]
    assert [
        recognizer.supported_language
        for recognizer in recognizer_registry.recognizers
        if recognizer.name == "ZipCodeRecognizer"
    ] == ["de"]
    assert [
        recognizer.supported_language
        for recognizer in recognizer_registry.recognizers
        if recognizer.name == "ExampleCustomRecognizer"
    ] == ["en", "es"]
    assert sorted(
        [
            recognizer.supported_language
            for recognizer in recognizer_registry.recognizers
            if recognizer.name == "SpacyRecognizer"
        ]
    ) == sorted(["en"])
    spanish_recognizer = [
        recognizer
        for recognizer in recognizer_registry.recognizers
        if recognizer.name == "ExampleCustomRecognizer"
        and recognizer.supported_language == "es"
    ][0]
    assert spanish_recognizer.context == ["tarjeta", "credito"]
    assert isinstance(engine.nlp_engine, SpacyNlpEngine)
    assert engine.nlp_engine.engine_name == "spacy"


def test_analyzer_engine_provider_configuration_file_missing_values_expect_defaults(mandatory_recognizers):
    test_yaml, _, _ = get_full_paths("conf/test_analyzer_engine_missing_values.yaml")
    provider = AnalyzerEngineProvider(test_yaml)
    engine = provider.create_engine()
    assert engine.supported_languages == ["de", "en", "es"]
    assert engine.default_score_threshold == 0
    recognizer_registry = engine.registry
    assert (
        recognizer_registry.global_regex_flags
        == re.DOTALL | re.MULTILINE | re.IGNORECASE
    )
    assert recognizer_registry.supported_languages == ["de", "en", "es"]
    names = [recognizer.name for recognizer in recognizer_registry.recognizers]
    for predefined_recognizer in mandatory_recognizers:
        assert predefined_recognizer in names
    assert isinstance(engine.nlp_engine, SpacyNlpEngine)
    assert engine.nlp_engine.engine_name == "spacy"


def test_analyzer_engine_provider_defaults(mandatory_recognizers):
    provider = AnalyzerEngineProvider()
    engine = provider.create_engine()
    assert engine.supported_languages == ["en"]
    assert engine.default_score_threshold == 0
    recognizer_registry = engine.registry
    assert (
        recognizer_registry.global_regex_flags
        == re.DOTALL | re.MULTILINE | re.IGNORECASE
    )
    assert recognizer_registry.supported_languages == ["en"]
    names = [recognizer.name for recognizer in recognizer_registry.recognizers]
    for predefined_recognizer in mandatory_recognizers:
        assert predefined_recognizer in names
    assert isinstance(engine.nlp_engine, SpacyNlpEngine)
    assert engine.nlp_engine.engine_name == "spacy"


def test_analyzer_engine_provider_with_files_per_provider():
    analyzer_yaml, nlp_engine_yaml, recognizer_registry_yaml = get_full_paths(
        "conf/simple_analyzer_engine.yaml",
        "conf/default.yaml",
        "conf/test_recognizer_registry.yaml",
    )

    provider = AnalyzerEngineProvider(
        analyzer_engine_conf_file=analyzer_yaml,
        nlp_engine_conf_file=nlp_engine_yaml,
        recognizer_registry_conf_file=recognizer_registry_yaml,
    )

    provider = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_yaml,
                                      nlp_engine_conf_file=nlp_engine_yaml,
                                      recognizer_registry_conf_file=recognizer_registry_yaml)

    analyzer_engine = provider.create_engine()

    # assert analyzer instance is correct
    assert analyzer_engine.supported_languages == ["en", "es"]
    assert analyzer_engine.default_score_threshold == 0.43

    # assert nlp engine is correct
    nlp_engine = analyzer_engine.nlp_engine
    assert isinstance(nlp_engine, SpacyNlpEngine)
    assert nlp_engine.nlp is not None
    assert nlp_engine.get_supported_languages() == ["en"]

    # assert recognizer registry is correct
    recognizer_registry = analyzer_engine.registry
    assert len(recognizer_registry.recognizers) == 6
    assert recognizer_registry.supported_languages == ["en", "es"]
