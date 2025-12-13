import re
from pathlib import Path
from typing import List

from presidio_analyzer import AnalyzerEngineProvider, RecognizerResult, PatternRecognizer
from presidio_analyzer.nlp_engine import SpacyNlpEngine, NlpArtifacts


from presidio_analyzer.predefined_recognizers import (
    AzureAILanguageRecognizer,
    CreditCardRecognizer,
    SpacyRecognizer,
    StanzaRecognizer,
)

import pytest


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


@pytest.mark.skipif(
    pytest.importorskip("azure"), reason="Optional dependency not installed"
)  # noqa: E501
def test_analyzer_engine_provider_with_azure_ai_language():
    analyzer_yaml, _, _ = get_full_paths(
        "conf/test_azure_ai_language_reco.yaml",
    )

    class MockAzureAiLanguageRecognizer(AzureAILanguageRecognizer):
        def analyze(
            self,
            text: str,
            entities: List[str] = None,
            nlp_artifacts: NlpArtifacts = None,
        ) -> List[RecognizerResult]:
            return [RecognizerResult(entity_type="PERSON", start=0, end=4, score=0.9)]

    provider = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_yaml)

    analyzer_engine = provider.create_engine()

    azure_ai_recognizers = [
        rec
        for rec in analyzer_engine.registry.recognizers
        if rec.name == "Azure AI Language PII"
    ]

    assert len(azure_ai_recognizers) == 1

    assert len(analyzer_engine.analyze("This is a test", language="en")) > 0

@pytest.mark.skipif(pytest.importorskip("azure"), reason="Optional dependency not installed") # noqa: E501
def test_analyzer_engine_provider_with_ahds():
    analyzer_yaml, _, _ = get_full_paths(
        "conf/test_ahds_reco.yaml",
    )
    from presidio_analyzer.predefined_recognizers import AzureHealthDeidRecognizer

    class MockAHDSDeidRecognizer(AzureHealthDeidRecognizer):
        def analyze(
            self,
            text: str,
            entities: List[str] = None,
            nlp_artifacts: NlpArtifacts = None,
        ) -> List[RecognizerResult]:
            return [RecognizerResult(entity_type="PATIENT", start=0, end=4, score=0.9)]

    provider = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_yaml)

    analyzer_engine = provider.create_engine()

    ahds_recognizers = [
        rec
        for rec in analyzer_engine.registry.recognizers
        if rec.name == "Azure Health Data Services de-identification"
    ]

    assert len(ahds_recognizers) == 1

    assert len(analyzer_engine.analyze("This is a test", language="en")) > 0
    


def test_analyzer_engine_provider_no_nlp_recognizer():
    analyzer_yaml, _, _ = get_full_paths(
        "conf/test_nlp_reco_disabled_conf.yaml",
    )

    provider = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_yaml)

    analyzer_engine = provider.create_engine()

    assert len(analyzer_engine.get_recognizers()) == 1
    recognizer = analyzer_engine.get_recognizers()[0]
    assert isinstance(recognizer, CreditCardRecognizer)

    assert len(analyzer_engine.analyze("My Credit card number is 4917300800000000", language="en")) > 0


def test_analyzer_engine_provider_no_nlp_recognizer_is_added():
    analyzer_yaml, _, _ = get_full_paths(
        "conf/test_no_nlp_reco_conf.yaml",
    )
    provider = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_yaml)

    analyzer_engine = provider.create_engine()

    assert len(analyzer_engine.get_recognizers()) == 2
    nlp_recognizer = [
        rec
        for rec in analyzer_engine.get_recognizers()
        if isinstance(rec, SpacyRecognizer)
    ]
    assert len(nlp_recognizer) == 1


def test_analyzer_engine_provider_no_nlp_recognizer_is_added_per_language():
    analyzer_yaml, _, _ = get_full_paths(
        "conf/test_no_nlp_reco_conf_multilingual.yaml",
    )
    provider = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_yaml)

    analyzer_engine = provider.create_engine()

    assert len(analyzer_engine.get_recognizers()) == 4 # Two CreditCardRecognizers and two SpacyRecognizers
    nlp_recognizers = [
        rec
        for rec in analyzer_engine.get_recognizers()
        if isinstance(rec, SpacyRecognizer)
    ]
    assert len(nlp_recognizers) == 2  # one per language
    assert set([rec.supported_language for rec in nlp_recognizers]) == {"en", "es"}


def test_analyzer_engine_provider_mismatch_between_nlp_engine_and_nlp_recognizer():
    analyzer_yaml, _, _ = get_full_paths(
        "conf/test_nlp_reco_does_not_match_engine.yaml",
    )

    with pytest.raises(ValueError):
        provider = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_yaml)
        analyzer_engine = provider.create_engine()


def test_analyzer_engine_provider_multiple_nlp_recognizers_raises_exception():
    analyzer_yaml, _, _ = get_full_paths(
        "conf/test_multiple_nlp_recognizers.yaml",
    )

    with pytest.raises(
        ValueError,
        match=f"Multiple NLP recognizers for language en found in the configuration. "
                f"Please remove the duplicates."):
        provider = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_yaml)
        analyzer_engine = provider.create_engine()


def test_analyzer_engine_provider_no_nlp_engine_or_provider_results_in_default_nlp_recognizer():
    analyzer_yaml, _, _ = get_full_paths(
        "conf/test_no_nlp_engine.yaml",
    )
    provider = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_yaml)

    analyzer_engine = provider.create_engine()

    assert len(analyzer_engine.get_recognizers()) == 2 # SpacyRecognizer, CreditCardRecognizer
    nlp_recognizer = [
        rec
        for rec in analyzer_engine.get_recognizers()
        if isinstance(rec, SpacyRecognizer)
    ]
    assert len(nlp_recognizer) == 1


@pytest.mark.skip_engine("stanza_en")
def test_analyzer_engine_stanza_without_recognizer_creates_recognizer():
    analyzer_yaml, _, _ = get_full_paths(
        "conf/test_stanza_without_recognizer.yaml",
    )
    provider = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_yaml)

    analyzer_engine = provider.create_engine()

    assert (
        len(analyzer_engine.get_recognizers()) == 3
    )  # StanzaRecognizer en, StanzaRecognizer es, CreditCardRecognizer
    nlp_recognizers = [
        rec
        for rec in analyzer_engine.get_recognizers()
        if isinstance(rec, StanzaRecognizer)
    ]
    assert len(nlp_recognizers) == 2
    supported_languages = {
        nlp_recognizers[0].supported_language,
        nlp_recognizers[1].supported_language,
    }
    assert supported_languages == {"en", "es"}

def test_analyzer_engine_provider_one_custom_recognizer():
    analyzer_yaml, _, _ = get_full_paths(
        "conf/custom_recognizer_yaml.yaml",
    )
    provider = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_yaml)

    analyzer_engine = provider.create_engine()
    assert len(analyzer_engine.get_recognizers()) == 1
    assert analyzer_engine.analyze("My zip code is 12345", language="en")[0].score == pytest.approx(0.4)


def test_analyzer_engine_provider_invalid_analyzer_conf_file():
    """Test that invalid analyzer configuration file path raises error."""
    with pytest.raises(ValueError):
        AnalyzerEngineProvider(analyzer_engine_conf_file="/nonexistent/path/file.yaml")


def test_analyzer_engine_provider_invalid_nlp_conf_file():
    """Test that invalid NLP engine configuration file path raises error."""
    with pytest.raises(ValueError):
        AnalyzerEngineProvider(nlp_engine_conf_file="/nonexistent/path/file.yaml")


def test_analyzer_engine_provider_invalid_registry_conf_file():
    """Test that invalid recognizer registry configuration file path raises error."""
    with pytest.raises(ValueError):
        AnalyzerEngineProvider(recognizer_registry_conf_file="/nonexistent/path/file.yaml")


def test_analyzer_engine_provider_get_configuration_with_nonexistent_file():
    """Test get_configuration falls back to default when file doesn't exist."""
    provider = AnalyzerEngineProvider()

    # Test with nonexistent file - should fall back to default
    config = provider.get_configuration("/tmp/nonexistent_config_file_12345.yaml")

    # Should return a valid configuration (the default one)
    assert config is not None
    assert isinstance(config, dict)


def test_analyzer_engine_provider_get_configuration_with_invalid_yaml():
    """Test get_configuration handles invalid YAML gracefully."""
    import tempfile
    import os

    # Create a temporary file with invalid YAML
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("invalid: yaml: content: [[[")
        temp_file = f.name

    try:
        provider = AnalyzerEngineProvider()
        config = provider.get_configuration(temp_file)

        # Should fall back to default configuration
        assert config is not None
        assert isinstance(config, dict)
    finally:
        os.unlink(temp_file)


def test_analyzer_engine_provider_get_full_conf_path():
    """Test _get_full_conf_path static method."""
    from pathlib import Path

    path = AnalyzerEngineProvider._get_full_conf_path()

    assert isinstance(path, Path)
    assert path.name == "default_analyzer.yaml"
    assert path.exists()


def test_analyzer_engine_provider_get_full_conf_path_custom_file():
    """Test _get_full_conf_path with custom filename."""
    from pathlib import Path

    path = AnalyzerEngineProvider._get_full_conf_path("custom_file.yaml")

    assert isinstance(path, Path)
    assert path.name == "custom_file.yaml"


def test_analyzer_engine_provider_configuration_property():
    """Test that configuration property is set correctly."""
    provider = AnalyzerEngineProvider()

    assert provider.configuration is not None
    assert isinstance(provider.configuration, dict)


def test_analyzer_engine_provider_nlp_engine_conf_file_property():
    """Test that nlp_engine_conf_file property is stored correctly."""
    test_yaml, nlp_yaml, _ = get_full_paths(
        "conf/simple_analyzer_engine.yaml",
        "conf/default.yaml",
    )

    provider = AnalyzerEngineProvider(
        analyzer_engine_conf_file=test_yaml,
        nlp_engine_conf_file=nlp_yaml,
    )

    assert provider.nlp_engine_conf_file == nlp_yaml


def test_analyzer_engine_provider_recognizer_registry_conf_file_property():
    """Test that recognizer_registry_conf_file property is stored correctly."""
    test_yaml, _, registry_yaml = get_full_paths(
        "conf/simple_analyzer_engine.yaml",
        None,
        "conf/test_recognizer_registry.yaml",
    )

    provider = AnalyzerEngineProvider(
        analyzer_engine_conf_file=test_yaml,
        recognizer_registry_conf_file=registry_yaml,
    )

    assert provider.recognizer_registry_conf_file == registry_yaml


def test_analyzer_engine_provider_load_nlp_engine_from_conf():
    """Test _load_nlp_engine with nlp_configuration in analyzer config."""
    analyzer_yaml, _, _ = get_full_paths("conf/test_analyzer_engine.yaml")

    provider = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_yaml)
    nlp_engine = provider._load_nlp_engine()

    assert nlp_engine is not None
    assert nlp_engine.engine_name == "spacy"


def test_analyzer_engine_provider_load_nlp_engine_default():
    """Test _load_nlp_engine falls back to default when no config provided."""
    provider = AnalyzerEngineProvider()
    nlp_engine = provider._load_nlp_engine()

    assert nlp_engine is not None
    assert isinstance(nlp_engine, SpacyNlpEngine)


def test_analyzer_engine_provider_load_recognizer_registry_from_embedded_config():
    """Test _load_recognizer_registry with embedded recognizer_registry in config."""
    analyzer_yaml, _, _ = get_full_paths("conf/test_analyzer_engine.yaml")

    provider = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_yaml)
    nlp_engine = provider._load_nlp_engine()

    registry = provider._load_recognizer_registry(
        supported_languages=["en"],
        nlp_engine=nlp_engine,
    )

    assert registry is not None
    assert len(registry.recognizers) > 0


def test_analyzer_engine_provider_load_recognizer_registry_default():
    """Test _load_recognizer_registry uses default when no config provided."""
    provider = AnalyzerEngineProvider()
    nlp_engine = provider._load_nlp_engine()

    registry = provider._load_recognizer_registry(
        supported_languages=["en"],
        nlp_engine=nlp_engine,
    )

    assert registry is not None
    assert len(registry.recognizers) > 0


def test_analyzer_engine_provider_create_engine_with_all_params():
    """Test create_engine with all configuration parameters."""
    analyzer_yaml, nlp_yaml, registry_yaml = get_full_paths(
        "conf/simple_analyzer_engine.yaml",
        "conf/default.yaml",
        "conf/test_recognizer_registry.yaml",
    )

    provider = AnalyzerEngineProvider(
        analyzer_engine_conf_file=analyzer_yaml,
        nlp_engine_conf_file=nlp_yaml,
        recognizer_registry_conf_file=registry_yaml,
    )

    engine = provider.create_engine()

    assert engine is not None
    assert engine.nlp_engine is not None
    assert engine.registry is not None
    assert len(engine.supported_languages) > 0


def test_analyzer_engine_provider_multiple_languages_support():
    """Test analyzer engine with multiple language support."""
    analyzer_yaml, _, _ = get_full_paths("conf/test_analyzer_engine.yaml")

    provider = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_yaml)
    engine = provider.create_engine()

    assert "en" in engine.supported_languages
    assert "de" in engine.supported_languages
    assert "es" in engine.supported_languages


def test_analyzer_engine_provider_default_score_threshold():
    """Test that default_score_threshold is properly set."""
    analyzer_yaml, _, _ = get_full_paths("conf/test_analyzer_engine.yaml")

    provider = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_yaml)
    engine = provider.create_engine()

    assert engine.default_score_threshold == 0.7


def test_analyzer_engine_provider_with_pathlib_path():
    """Test AnalyzerEngineProvider works with pathlib.Path objects."""
    from pathlib import Path

    analyzer_yaml, _, _ = get_full_paths("conf/simple_analyzer_engine.yaml")
    analyzer_path = Path(analyzer_yaml)

    provider = AnalyzerEngineProvider(analyzer_engine_conf_file=analyzer_path)
    engine = provider.create_engine()

    assert engine is not None


def test_analyzer_engine_provider_configuration_logging(caplog):
    """Test that configuration loading logs appropriate messages."""
    import logging

    with caplog.at_level(logging.INFO):
        provider = AnalyzerEngineProvider()
        _ = provider.create_engine()

    # Check that some logging occurred
    assert len(caplog.records) > 0


