import pytest

from presidio_analyzer import (
    AnalyzerEngine,
    PatternRecognizer,
    Pattern,
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
    return AppTracerMock(enable_decision_process=True)


@pytest.fixture(scope="module")
def loaded_analyzer_engine(loaded_registry, app_tracer):
    mock_nlp_artifacts = NlpArtifacts([], [], [], [], None, "en")
    analyzer_engine = AnalyzerEngine(
        loaded_registry,
        NlpEngineMock(stopwords=[], punct_words=[], nlp_artifacts=mock_nlp_artifacts),
        app_tracer=app_tracer,
        log_decision_process=True,
    )
    return analyzer_engine


@pytest.fixture(scope="module")
def unit_test_guid():
    return "00000000-0000-0000-0000-000000000000"


@pytest.fixture(scope="module")
def nlp_engine(nlp_engines):
    return nlp_engines["spacy_en"]


def test_simple():
    dic = {
        "text": "John Smith drivers license is AC432223",
        "language": "en",
        "score_threshold": 0.7,
        "entities": ["CRYPTO", "NRP", "DATE_TIME", "LOCATION", "PERSON"],
    }

    analyzer = AnalyzerEngine()
    analyzer.analyze(**dic)


def test_when_analyze_with_predefined_recognizers_then_return_results(
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


def test_when_analyze_with_multiple_predefined_recognizers_then_succeed(
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
    medium_regex_score = 0.4
    context_similarity_factor = 0.35  # PatternRecognizer.CONTEXT_SIMILARITY_FACTOR
    assert_result(results[0], "CREDIT_CARD", 14, 33, max_score)
    expected_score = medium_regex_score + context_similarity_factor
    assert_result(results[1], "PHONE_NUMBER", 48, 59, expected_score)


def test_when_analyze_with_empty_text_then_no_results(
    loaded_analyzer_engine, unit_test_guid
):
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


def test_when_analyze_with_unsupported_language_then_fail(
    loaded_analyzer_engine, unit_test_guid
):
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


def test_when_analyze_two_entities_embedded_then_return_results(nlp_engine):
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

    # Name with driver license in it
    text = "My name is John 1234567 Doe"
    results = analyzer.analyze(text=text, language="en", score_threshold=0)

    # currently we only remove duplicates when the two have the same entity type
    assert len(results) == 2


def test_when_analyze_added_pattern_recognizer_then_succeed(unit_test_guid):
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


def test_when_removed_pattern_recognizer_then_doesnt_work(unit_test_guid):
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


def test_when_analyze_with_language_then_returns_correct_response(
    loaded_analyzer_engine,
):
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


def test_when_entities_is_none_then_return_all_fields(loaded_registry):
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


def test_when_entities_is_none_all_recognizers_loaded_then_return_all_fields(
    nlp_engine,
):
    analyze_engine = AnalyzerEngine(
        registry=RecognizerRegistry(), nlp_engine=nlp_engine
    )
    threshold = 0
    text = "My name is Sharon and I live in Seattle." "Domain: microsoft.com "
    response = analyze_engine.analyze(
        text=text, score_threshold=threshold, language="en"
    )
    returned_entities = [response.entity_type for response in response]

    assert response is not None
    assert "PERSON" in returned_entities
    assert "LOCATION" in returned_entities
    assert "DOMAIN_NAME" in returned_entities


def test_when_analyze_then_apptracer_has_value(
    loaded_registry, unit_test_guid, nlp_engine
):
    text = "My name is Bart Simpson, and Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"  # noqa E501
    language = "en"
    entities = ["CREDIT_CARD", "PHONE_NUMBER", "PERSON"]
    app_tracer_mock = AppTracerMock(enable_decision_process=True)
    analyzer_engine_with_spacy = AnalyzerEngine(
        loaded_registry,
        app_tracer=app_tracer_mock,
        log_decision_process=True,
        nlp_engine=nlp_engine,
    )
    results = analyzer_engine_with_spacy.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language=language,
        return_decision_process=True,
    )
    assert len(results) == 3
    for result in results:
        assert result.analysis_explanation is not None
    assert app_tracer_mock.get_msg_counter() == 2
    assert app_tracer_mock.get_last_trace() is not None


def test_when_threshold_is_zero_then_all_results_pass(loaded_registry, unit_test_guid):
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


def test_when_threshold_is_more_than_half_then_only_credit_card_passes(
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


def test_when_default_threshold_is_more_than_half_then_only_one_passes(
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


def test_when_default_threshold_is_zero_then_all_results_pass(
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


def test_when_get_supported_fields_then_return_all_languages(
    mock_registry, unit_test_guid, nlp_engine
):
    analyzer = AnalyzerEngine(registry=mock_registry, nlp_engine=nlp_engine)
    entities = analyzer.get_supported_entities()

    assert len(entities) == 3
    assert "CREDIT_CARD" in entities
    assert "DOMAIN_NAME" in entities
    assert "PHONE_NUMBER" in entities


def test_when_get_supported_fields_specific_language_then_return_single_result(
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


def test_when_get_recognizers_then_returns_supported_language():
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


def test_when_add_recognizer_then_also_outputs_others(nlp_engine):
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


def test_when_given_no_decision_process_requested_then_response_contains_no_analysis(
    loaded_analyzer_engine, unit_test_guid
):
    text = "John Smith drivers license is AC432223"
    language = "en"
    return_decision_process = False
    results = loaded_analyzer_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        return_decision_process=return_decision_process,
        language=language,
    )

    assert len(results) == 1
    assert results[0].analysis_explanation is None


def test_given_decision_process_requested_then_response_contains_analysis(
    loaded_analyzer_engine, unit_test_guid
):
    text = "John Smith drivers license is AC432223"
    language = "en"
    return_decision_process = True
    results = loaded_analyzer_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        return_decision_process=return_decision_process,
        language=language,
    )

    assert len(results) == 1
    assert results[0].analysis_explanation is not None


def test_when_read_test_spacy_nlp_conf_file_then_returns_spacy_nlp_engine(
    mock_registry,
):
    engine = AnalyzerEngine(registry=mock_registry)

    assert isinstance(engine.nlp_engine, SpacyNlpEngine)
    assert engine.nlp_engine.nlp is not None


def test_when_ad_hoc_pattern_recognizer_is_added_then_result_contains_result(
    loaded_analyzer_engine, zip_code_recognizer
):
    text = "John Smith drivers license is AC432223 and his zip code is 10023"

    responses = loaded_analyzer_engine.analyze(
        text=text, language="en", ad_hoc_recognizers=[zip_code_recognizer]
    )

    detected_entities = [response.entity_type for response in responses]
    assert "ZIP" in detected_entities


def test_when_ad_hoc_deny_list_recognizer_is_added_then_result_contains_result(
    loaded_analyzer_engine,
):
    text = "Mr. John Smith's drivers license is AC432223"

    mr_recognizer = PatternRecognizer(supported_entity="MR", deny_list=["Mr.", "Mr"])

    responses = loaded_analyzer_engine.analyze(
        text=text, language="en", ad_hoc_recognizers=[mr_recognizer]
    )

    detected_entities = [response.entity_type for response in responses]
    assert "MR" in detected_entities


def test_when_ad_hoc_deny_list_recognizer_is_added_then_result_does_not_persist(
    loaded_analyzer_engine,
):
    text = "Mr. John Smith's drivers license is AC432223"

    mr_recognizer = PatternRecognizer(supported_entity="MR", deny_list=["Mr.", "Mr"])

    responses1 = loaded_analyzer_engine.analyze(
        text=text, language="en", ad_hoc_recognizers=[mr_recognizer]
    )
    responses2 = loaded_analyzer_engine.analyze(text=text, language="en")

    detected_entities1 = [response.entity_type for response in responses1]
    assert "MR" in detected_entities1

    detected_entities2 = [response.entity_type for response in responses2]
    assert "MR" not in detected_entities2


def test_when_ad_hoc_deny_list_recognizer_contains_both_regex_and_deny_list(
    loaded_analyzer_engine, zip_code_deny_list_recognizer
):
    text = "Mr. John Smith's zip code is 10023 or 999"

    responses = loaded_analyzer_engine.analyze(
        text=text, language="en", ad_hoc_recognizers=[zip_code_deny_list_recognizer]
    )

    detected_zips = [
        response.entity_type for response in responses if response.entity_type == "ZIP"
    ]
    assert len(detected_zips) == 2


def test_entities_filter_for_ad_hoc_removes_recognizer(loaded_analyzer_engine):
    text = "Mr. John Smith's zip code is 10002"

    mr_recognizer = PatternRecognizer(supported_entity="MR", deny_list=["Mr.", "Mr"])
    responses1 = loaded_analyzer_engine.analyze(
        text=text, language="en", ad_hoc_recognizers=[mr_recognizer]
    )
    responses2 = loaded_analyzer_engine.analyze(
        text=text,
        language="en",
        ad_hoc_recognizers=[mr_recognizer],
        entities=["PERSON"],
    )

    assert "MR" in [resp.entity_type for resp in responses1]
    assert "MR" not in [resp.entity_type for resp in responses2]


def test_ad_hoc_with_context_support_higher_confidence(nlp_engine, zip_code_recognizer):
    text = "Mr. John Smith's zip code is 10023"
    analyzer_engine = AnalyzerEngine(nlp_engine=nlp_engine)

    responses1 = analyzer_engine.analyze(
        text=text, language="en", ad_hoc_recognizers=[zip_code_recognizer]
    )

    zip_code_recognizer.context = ["zip", "code"]
    responses2 = analyzer_engine.analyze(
        text=text, language="en", ad_hoc_recognizers=[zip_code_recognizer]
    )

    zip_result_no_context = [resp for resp in responses1 if resp.entity_type == "ZIP"]
    zip_result_with_context = [resp for resp in responses2 if resp.entity_type == "ZIP"]

    assert zip_result_no_context[0].score < zip_result_with_context[0].score


def test_ad_hoc_when_no_other_recognizers_are_requested_returns_only_ad_hoc_results(
    loaded_analyzer_engine, zip_code_recognizer
):
    text = "Mr. John Smith's zip code is 10023"

    responses = loaded_analyzer_engine.analyze(
        text=text,
        language="en",
        ad_hoc_recognizers=[zip_code_recognizer],
        entities=["ZIP"],
    )

    assert "ZIP" in [resp.entity_type for resp in responses]
