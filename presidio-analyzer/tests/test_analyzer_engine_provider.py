import re
from pathlib import Path
from typing import List

from presidio_analyzer import AnalyzerEngineProvider, RecognizerResult
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


def test_analyzer_engine_provider_configuration_file_missing_values_expect_defaults(
    mandatory_recognizers,
):
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
