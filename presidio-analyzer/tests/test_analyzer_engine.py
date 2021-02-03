from pathlib import Path
from typing import List

import pytest

from presidio_analyzer import (
    AnalyzerEngine,
    PatternRecognizer,
    Pattern,
    RecognizerResult,
    RecognizerRegistry,
)
from presidio_analyzer.nlp_engine import (
    NlpArtifacts,
    SpacyNlpEngine,
)

# noqa: F401
from tests import assert_result
from tests.mocks import NlpEngineMock, AppTracerMock, RecognizerRegistryMock


@pytest.fixture(scope="module")
def app_tracer():
    return AppTracerMock(enable_interpretability=True)


@pytest.fixture(scope="module")
def loaded_analyzer_engine(loaded_registry, app_tracer):
    mock_nlp_artifacts = NlpArtifacts([], [], [], [], None, "en")
    analyzer_engine = AnalyzerEngine(
        loaded_registry,
        NlpEngineMock(stopwords=[], punct_words=[], nlp_artifacts=mock_nlp_artifacts),
        app_tracer=app_tracer,
        enable_trace_pii=True,
    )
    return analyzer_engine


@pytest.fixture(scope="module")
def unit_test_guid():
    return "00000000-0000-0000-0000-000000000000"


@pytest.fixture(scope="module")
def nlp_engine(nlp_engines):
    return nlp_engines["spacy_en"]


def test_analyze_with_predefined_recognizers_return_results(
    loaded_analyzer_engine, unit_test_guid, max_score
):
    text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
    language = "en"
    entities = ["CREDIT_CARD"]
    results = loaded_analyzer_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language=language,
    )

    assert len(results) == 1
    assert_result(results[0], "CREDIT_CARD", 14, 33, max_score)


def test_analyze_with_multiple_predefined_recognizers(
    loaded_registry, unit_test_guid, nlp_engine, max_score
):
    text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
    language = "en"
    entities = ["CREDIT_CARD", "PHONE_NUMBER"]

    analyzer_engine_with_spacy = AnalyzerEngine(
        registry=loaded_registry, nlp_engine=nlp_engine
    )
    results = analyzer_engine_with_spacy.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language=language,
    )

    assert len(results) == 2
    medium_regex_score = 0.5  # see UsPhoneRecognizer.PATTERNS
    context_similarity_factor = 0.35  # PatternRecognizer.CONTEXT_SIMILARITY_FACTOR
    assert_result(results[0], "CREDIT_CARD", 14, 33, max_score)
    expected_score = medium_regex_score + context_similarity_factor
    assert_result(results[1], "PHONE_NUMBER", 48, 59, expected_score)


def test_analyze_with_empty_text(loaded_analyzer_engine, unit_test_guid):
    language = "en"
    text = ""
    entities = ["CREDIT_CARD", "PHONE_NUMBER"]
    results = loaded_analyzer_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language=language,
    )

    assert len(results) == 0


def test_analyze_with_unsupported_language(loaded_analyzer_engine, unit_test_guid):
    with pytest.raises(ValueError):
        language = "de"
        text = ""
        entities = ["CREDIT_CARD", "PHONE_NUMBER"]
        loaded_analyzer_engine.analyze(
            correlation_id=unit_test_guid,
            text=text,
            entities=entities,
            language=language,
        )


def test_analyze_two_entities_embedded(nlp_engine):
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

    # Name with driver license in it
    text = "My name is John 1234567 Doe"
    results = analyzer.analyze(text=text, language="en", score_threshold=0)

    # currently we only remove duplicates when the two have the same entity type
    assert len(results) == 2


def test_analyze_added_pattern_recognizer_works(unit_test_guid):
    pattern = Pattern("rocket pattern", r"\W*(rocket)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "ROCKET", name="Rocket recognizer", patterns=[pattern]
    )

    mock_recognizer_registry = RecognizerRegistryMock()

    # Make sure the analyzer doesn't get this entity
    analyze_engine = AnalyzerEngine(
        registry=mock_recognizer_registry,
        nlp_engine=NlpEngineMock(),
    )
    text = "rocket is my favorite transportation"
    entities = ["CREDIT_CARD", "ROCKET"]

    results = analyze_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language="en",
    )

    assert len(results) == 0

    # Add a new recognizer for the word "rocket" (case insensitive)
    mock_recognizer_registry.add_recognizer(pattern_recognizer)

    # Check that the entity is recognized:
    results = analyze_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language="en",
    )

    assert len(results) == 1
    assert_result(results[0], "ROCKET", 0, 7, 0.8)


def test_removed_pattern_recognizer_doesnt_work(unit_test_guid):
    pattern = Pattern("spaceship pattern", r"\W*(spaceship)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "SPACESHIP", name="Spaceship recognizer", patterns=[pattern]
    )

    mock_recognizer_registry = RecognizerRegistryMock()

    # Make sure the analyzer doesn't get this entity
    analyze_engine = AnalyzerEngine(
        registry=mock_recognizer_registry,
        nlp_engine=NlpEngineMock(),
    )
    text = "spaceship is my favorite transportation"
    entities = ["CREDIT_CARD", "SPACESHIP"]

    results = analyze_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language="en",
    )

    assert len(results) == 0

    # Add a new recognizer for the word "rocket" (case insensitive)
    mock_recognizer_registry.add_recognizer(pattern_recognizer)
    # Check that the entity is recognized:
    results = analyze_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language="en",
    )
    assert len(results) == 1
    assert_result(results[0], "SPACESHIP", 0, 10, 0.8)

    # Remove recognizer
    mock_recognizer_registry.remove_recognizer("Spaceship recognizer")
    # Test again to see we didn't get any results
    results = analyze_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language="en",
    )

    assert len(results) == 0


def test_analyze_with_language_returns_correct_response(loaded_analyzer_engine):
    language = "en"
    entities = ["CREDIT_CARD"]
    min_score = 0.5
    text = "My credit card number is 4916994465041084"
    response = loaded_analyzer_engine.analyze(
        text=text,
        language=language,
        entities=entities,
        score_threshold=min_score,
    )

    assert response is not None


def test_analyze_when_entities_is_none_return_all_fields(loaded_registry):
    analyze_engine = AnalyzerEngine(
        registry=loaded_registry, nlp_engine=NlpEngineMock()
    )
    threshold = 0
    text = (
        " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090 "
        "Domain: microsoft.com"
    )
    response = analyze_engine.analyze(
        text=text, score_threshold=threshold, language="en"
    )
    returned_entities = [response.entity_type for response in response]

    assert response is not None
    assert "CREDIT_CARD" in returned_entities
    assert "PHONE_NUMBER" in returned_entities
    assert "DOMAIN_NAME" in returned_entities


def test_analyze_when_entities_is_none_all_recognizers_loaded_return_all_fields(
    nlp_engine,
):
    analyze_engine = AnalyzerEngine(
        registry=RecognizerRegistry(), nlp_engine=nlp_engine
    )
    threshold = 0
    text = "My name is David and I live in Seattle." "Domain: microsoft.com "
    response = analyze_engine.analyze(
        text=text, score_threshold=threshold, language="en"
    )
    returned_entities = [response.entity_type for response in response]

    assert response is not None
    assert "PERSON" in returned_entities
    assert "LOCATION" in returned_entities
    assert "DOMAIN_NAME" in returned_entities


def test_analyze_when_analyze_then_apptracer_has_value(
    loaded_registry, unit_test_guid, nlp_engine
):
    text = "My name is Bart Simpson, and Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"  # noqa E501
    language = "en"
    entities = ["CREDIT_CARD", "PHONE_NUMBER", "PERSON"]
    app_tracer_mock = AppTracerMock(enable_interpretability=True)
    analyzer_engine_with_spacy = AnalyzerEngine(
        loaded_registry,
        app_tracer=app_tracer_mock,
        enable_trace_pii=True,
        nlp_engine=nlp_engine,
    )
    results = analyzer_engine_with_spacy.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language=language,
        trace=True,
    )
    assert len(results) == 3
    for result in results:
        assert result.analysis_explanation is not None
    assert app_tracer_mock.get_msg_counter() == 2
    assert app_tracer_mock.get_last_trace() is not None


def test_when_threshold_is_zero_all_results_pass(loaded_registry, unit_test_guid):
    text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
    language = "en"
    entities = ["CREDIT_CARD", "PHONE_NUMBER"]

    # This analyzer engine is different from the global one, as this one
    # also loads SpaCy so it can detect the phone number entity

    analyzer_engine = AnalyzerEngine(
        registry=loaded_registry, nlp_engine=NlpEngineMock()
    )
    results = analyzer_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language=language,
        score_threshold=0,
    )

    assert len(results) == 2


def test_when_threshold_is_more_than_half_only_credit_card_passes(
    loaded_registry, unit_test_guid
):
    text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
    language = "en"
    entities = ["CREDIT_CARD", "PHONE_NUMBER"]

    # This analyzer engine is different from the global one, as this one
    # also loads SpaCy so it can detect the phone number entity

    analyzer_engine = AnalyzerEngine(
        registry=loaded_registry, nlp_engine=NlpEngineMock()
    )
    results = analyzer_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language=language,
        score_threshold=0.51,
    )

    assert len(results) == 1


def test_when_default_threshold_is_more_than_half_only_one_passes(
    loaded_registry, unit_test_guid
):
    text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
    language = "en"
    entities = ["CREDIT_CARD", "PHONE_NUMBER"]

    # This analyzer engine is different from the global one, as this one
    # also loads SpaCy so it can detect the phone number entity

    analyzer_engine = AnalyzerEngine(
        registry=loaded_registry,
        nlp_engine=NlpEngineMock(),
        default_score_threshold=0.7,
    )
    results = analyzer_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language=language,
    )

    assert len(results) == 1


def test_when_default_threshold_is_zero_all_results_pass(
    loaded_registry, unit_test_guid
):
    text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
    language = "en"
    entities = ["CREDIT_CARD", "PHONE_NUMBER"]

    # This analyzer engine is different from the global one, as this one
    # also loads SpaCy so it can detect the phone number entity

    analyzer_engine = AnalyzerEngine(
        registry=loaded_registry, nlp_engine=NlpEngineMock()
    )
    results = analyzer_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language=language,
    )

    assert len(results) == 2


@pytest.mark.slow
def test_demo_text(unit_test_guid, nlp_engine):
    dir_path = Path(__file__).resolve().parent
    with open(Path(dir_path, "data", "demo.txt"), encoding="utf-8") as f:
        text_into_rows = f.read().split("\n")

    text_into_rows = [txt.strip() for txt in text_into_rows]
    text = " ".join(text_into_rows)
    language = "en"

    analyzer_engine = AnalyzerEngine(
        default_score_threshold=0.35, nlp_engine=nlp_engine
    )
    results = analyzer_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=None,
        language=language,
    )

    def replace_with_entity_name(original_text: str, responses: List[RecognizerResult]):
        """
        Performs replacements for every entity with its entity type
        """
        delta = 0
        new_text = original_text
        responses = sorted(responses, key=lambda x: x.start)
        for i, resp in enumerate(responses):
            # check if this response is already contained in a previous one
            if len([prev for prev in responses[:i] if resp.contained_in(prev)]) > 0:
                continue
            start = resp.start + delta
            end = resp.end + delta
            entity_text = original_text[resp.start : resp.end]
            entity_type = resp.entity_type

            new_text = f"{new_text[:start]}<{entity_type}>{new_text[end:]}"
            delta += len(entity_type) + 2 - len(entity_text)

        return new_text

    actual_anonymized_text = replace_with_entity_name(text, results)

    for result in results:
        text_slice = slice(result.start, result.end)
        print(
            "Entity = {}, Text = {}, Score={}, Start={}, End={}".format(
                result.entity_type,
                text[text_slice],
                result.score,
                result.start,
                result.end,
            )
        )

    with open(Path(dir_path, "data", "demo_anonymized.txt"), encoding="utf-8") as f_exp:
        text_into_rows = f_exp.read().split("\n")

    text_into_rows = [txt.strip() for txt in text_into_rows]
    expected_anonymized_text = " ".join(text_into_rows)

    #    assert len(results) == 19
    assert expected_anonymized_text == actual_anonymized_text


def test_get_supported_fields_all_languages(mock_registry, unit_test_guid, nlp_engine):
    analyzer = AnalyzerEngine(registry=mock_registry, nlp_engine=nlp_engine)
    entities = analyzer.get_supported_entities()

    assert len(entities) == 3
    assert "CREDIT_CARD" in entities
    assert "DOMAIN_NAME" in entities
    assert "PHONE_NUMBER" in entities


def test_get_supported_fields_specific_language(
    loaded_registry, unit_test_guid, nlp_engine
):
    pattern = Pattern("rocket pattern", r"\W*(rocket)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "ROCKET",
        name="Rocket recognizer RU",
        patterns=[pattern],
        supported_language="ru",
    )

    analyzer = AnalyzerEngine(registry=loaded_registry, nlp_engine=nlp_engine)
    analyzer.registry.add_recognizer(pattern_recognizer)
    entities = analyzer.get_supported_entities(language="ru")

    assert len(entities) == 1
    assert "ROCKET" in entities


def test_get_recognizers_returns_supported_language():
    pattern = Pattern("rocket pattern", r"\W*(rocket)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "ROCKET",
        name="Rocket recognizer RU",
        patterns=[pattern],
        supported_language="ru",
    )
    mock_recognizer_registry = RecognizerRegistryMock()
    mock_recognizer_registry.add_recognizer(pattern_recognizer)
    analyze_engine = AnalyzerEngine(
        registry=mock_recognizer_registry,
        nlp_engine=NlpEngineMock(),
    )
    response = analyze_engine.get_recognizers(language="ru")
    # there is only 1 mocked russian recognizer
    assert len(response) == 1


def test_add_recognizer_also_outputs_others(nlp_engine):
    pattern = Pattern("rocket pattern", r"\W*(rocket)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "ROCKET",
        name="Rocket recognizer",
        patterns=[pattern],
        supported_language="en",
    )
    registry = RecognizerRegistry()
    registry.add_recognizer(pattern_recognizer)
    registry.load_predefined_recognizers()

    assert len(registry.recognizers) > 1

    analyzer = AnalyzerEngine(registry=registry, nlp_engine=nlp_engine)

    text = "Michael Jones has a rocket"

    results = analyzer.analyze(text=text, language="en")
    assert len(results) == 2


def test_given_no_interpretability_requested_then_response_contains_no_analysis(
    loaded_analyzer_engine, unit_test_guid
):
    text = "John Smith drivers license is AC432223"
    language = "en"
    remove_interpretability_response = True
    results = loaded_analyzer_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        remove_interpretability_response=remove_interpretability_response,
        language=language,
    )

    assert len(results) == 1
    assert results[0].analysis_explanation is None


def test_given_interpretability_requested_then_response_contains_analysis(
    loaded_analyzer_engine, unit_test_guid
):
    text = "John Smith drivers license is AC432223"
    language = "en"
    remove_interpretability_response = False
    results = loaded_analyzer_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        remove_interpretability_response=remove_interpretability_response,
        language=language,
    )

    assert len(results) == 1
    assert results[0].analysis_explanation is not None


def test_read_test_spacy_nlp_conf_file_returns_spacy_nlp_engine(mock_registry):
    engine = AnalyzerEngine(registry=mock_registry)

    assert isinstance(engine.nlp_engine, SpacyNlpEngine)
    assert engine.nlp_engine.nlp is not None
