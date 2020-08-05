import hashlib

import pytest

from presidio_analyzer import (
    AnalyzerEngine,
    PatternRecognizer,
    Pattern,
    RecognizerResult,
    RecognizerRegistry,
    AnalysisExplanation,
)
from presidio_analyzer import PresidioLogger
from presidio_analyzer.protobuf_models.analyze_pb2 import (
    AnalyzeRequest,
    RecognizersAllRequest,
)
from presidio_analyzer.nlp_engine import NlpArtifacts
from presidio_analyzer.predefined_recognizers import (
    CreditCardRecognizer,
    UsPhoneRecognizer,
    DomainRecognizer,
)
from presidio_analyzer.recognizer_registry.recognizers_store_api import (
    RecognizerStoreApi,
)  # noqa: F401
from tests import assert_result
from tests.mocks import NlpEngineMock, AppTracerMock

logger = PresidioLogger()


class RecognizerStoreApiMock(RecognizerStoreApi):
    """
    A mock that acts as a recognizers store, allows to add and get recognizers
    """

    def __init__(self):
        self.latest_hash = ""
        self.recognizers = []

    def get_latest_hash(self):
        return self.latest_hash

    def get_all_recognizers(self):
        return self.recognizers

    def add_custom_pattern_recognizer(self, new_recognizer, skip_hash_update=False):
        patterns = []
        for pat in new_recognizer.patterns:
            patterns.extend([Pattern(pat.name, pat.regex, pat.score)])
        new_custom_recognizer = PatternRecognizer(
            name=new_recognizer.name,
            supported_entity=new_recognizer.supported_entities[0],
            supported_language=new_recognizer.supported_language,
            black_list=new_recognizer.black_list,
            context=new_recognizer.context,
            patterns=patterns,
        )
        self.recognizers.append(new_custom_recognizer)

        if skip_hash_update:
            return

        m = hashlib.md5()
        for recognizer in self.recognizers:
            m.update(recognizer.name.encode("utf-8"))
        self.latest_hash = m.digest()

    def remove_recognizer(self, name):
        for i in self.recognizers:
            if i.name == name:
                self.recognizers.remove(i)

        m = hashlib.md5()
        for recognizer in self.recognizers:
            m.update(recognizer.name.encode("utf-8"))
        self.latest_hash = m.digest()


class MockRecognizerRegistry(RecognizerRegistry):
    """
    A mock that acts as a recognizers registry
    """

    def load_recognizers(self, path):
        #   TODO: Change the code to dynamic loading -
        # Task #598:  Support loading of the pre-defined recognizers
        # from the given path.
        self.recognizers.extend(
            [CreditCardRecognizer(), UsPhoneRecognizer(), DomainRecognizer()]
        )


@pytest.fixture(scope="module")
def loaded_registry():
    return MockRecognizerRegistry(RecognizerStoreApiMock())


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
        all_fields=False,
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
        all_fields=False,
    )

    assert len(results) == 2
    medium_regex_score = 0.5  # see UsPhoneRecognizer.PATTERNS
    context_similarity_factor = 0.35  # PatternRecognizer.CONTEXT_SIMILARITY_FACTOR
    assert_result(results[0], "CREDIT_CARD", 14, 33, max_score)
    expected_score = medium_regex_score + context_similarity_factor
    assert_result(results[1], "PHONE_NUMBER", 48, 59, expected_score)


def test_analyze_without_entities(loaded_analyzer_engine, unit_test_guid):
    with pytest.raises(ValueError):
        language = "en"
        text = " Credit card: 4095-2609-9393-4932,  my name is  John Oliver, DateTime: September 18 Domain: microsoft.com"  # noqa E501
        entities = []
        loaded_analyzer_engine.analyze(
            correlation_id=unit_test_guid,
            text=text,
            entities=entities,
            language=language,
            all_fields=False,
        )


def test_analyze_with_empty_text(loaded_analyzer_engine, unit_test_guid):
    language = "en"
    text = ""
    entities = ["CREDIT_CARD", "PHONE_NUMBER"]
    results = loaded_analyzer_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language=language,
        all_fields=False,
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
            all_fields=False,
        )


def test_remove_duplicates():
    # test same result with different score will return only the highest
    arr = [
        RecognizerResult(
            start=0,
            end=5,
            score=0.1,
            entity_type="x",
            analysis_explanation=AnalysisExplanation(
                recognizer="test",
                original_score=0,
                pattern_name="test",
                pattern="test",
                validation_result=None,
            ),
        ),
        RecognizerResult(
            start=0,
            end=5,
            score=0.5,
            entity_type="x",
            analysis_explanation=AnalysisExplanation(
                recognizer="test",
                original_score=0,
                pattern_name="test",
                pattern="test",
                validation_result=None,
            ),
        ),
    ]
    results = AnalyzerEngine._AnalyzerEngine__remove_duplicates(arr)
    assert len(results) == 1
    assert results[0].score == 0.5
    # TODO: add more cases with bug:
    # bug# 597: Analyzer remove duplicates doesn't handle all cases of one
    #           result as a substring of the other


def test_remove_duplicates_different_entity_no_removal():
    # test same result with different score will return only the highest
    arr = [
        RecognizerResult(
            start=0,
            end=5,
            score=0.1,
            entity_type="x",
            analysis_explanation=AnalysisExplanation(
                recognizer="test",
                original_score=0,
                pattern_name="test",
                pattern="test",
                validation_result=None,
            ),
        ),
        RecognizerResult(
            start=0,
            end=5,
            score=0.5,
            entity_type="y",
            analysis_explanation=AnalysisExplanation(
                recognizer="test",
                original_score=0,
                pattern_name="test",
                pattern="test",
                validation_result=None,
            ),
        ),
    ]
    results = AnalyzerEngine._AnalyzerEngine__remove_duplicates(arr)
    assert len(results) == 2


def test_added_pattern_recognizer_works(unit_test_guid):
    pattern = Pattern("rocket pattern", r"\W*(rocket)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "ROCKET", name="Rocket recognizer", patterns=[pattern]
    )

    # Make sure the analyzer doesn't get this entity
    recognizers_store_api_mock = RecognizerStoreApiMock()
    analyze_engine = AnalyzerEngine(
        registry=MockRecognizerRegistry(recognizers_store_api_mock),
        nlp_engine=NlpEngineMock(),
    )
    text = "rocket is my favorite transportation"
    entities = ["CREDIT_CARD", "ROCKET"]

    results = analyze_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language="en",
        all_fields=False,
    )

    assert len(results) == 0

    # Add a new recognizer for the word "rocket" (case insensitive)
    recognizers_store_api_mock.add_custom_pattern_recognizer(pattern_recognizer)

    # Check that the entity is recognized:
    results = analyze_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language="en",
        all_fields=False,
    )

    assert len(results) == 1
    assert_result(results[0], "ROCKET", 0, 7, 0.8)


def test_removed_pattern_recognizer_doesnt_work(unit_test_guid):
    pattern = Pattern("spaceship pattern", r"\W*(spaceship)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "SPACESHIP", name="Spaceship recognizer", patterns=[pattern]
    )

    # Make sure the analyzer doesn't get this entity
    recognizers_store_api_mock = RecognizerStoreApiMock()
    analyze_engine = AnalyzerEngine(
        registry=MockRecognizerRegistry(recognizers_store_api_mock),
        nlp_engine=NlpEngineMock(),
    )
    text = "spaceship is my favorite transportation"
    entities = ["CREDIT_CARD", "SPACESHIP"]

    results = analyze_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language="en",
        all_fields=False,
    )

    assert len(results) == 0

    # Add a new recognizer for the word "rocket" (case insensitive)
    recognizers_store_api_mock.add_custom_pattern_recognizer(pattern_recognizer)
    # Check that the entity is recognized:
    results = analyze_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language="en",
        all_fields=False,
    )
    assert len(results) == 1
    assert_result(results[0], "SPACESHIP", 0, 10, 0.8)

    # Remove recognizer
    recognizers_store_api_mock.remove_recognizer("Spaceship recognizer")
    # Test again to see we didn't get any results
    results = analyze_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=entities,
        language="en",
        all_fields=False,
    )

    assert len(results) == 0


def test_apply_with_language_returns_correct_response(loaded_analyzer_engine):
    request = AnalyzeRequest()
    request.analyzeTemplate.language = "en"
    request.analyzeTemplate.resultsScoreThreshold = 0
    new_field = request.analyzeTemplate.fields.add()
    new_field.name = "CREDIT_CARD"
    new_field.minScore = "0.5"
    request.text = "My credit card number is 4916994465041084"
    response = loaded_analyzer_engine.Apply(request, None)

    assert response.analyzeResults is not None


def test_apply_with_no_language_returns_default(loaded_analyzer_engine):
    request = AnalyzeRequest()
    request.analyzeTemplate.language = ""
    request.analyzeTemplate.resultsScoreThreshold = 0
    new_field = request.analyzeTemplate.fields.add()
    new_field.name = "CREDIT_CARD"
    new_field.minScore = "0.5"
    request.text = "My credit card number is 4916994465041084"
    response = loaded_analyzer_engine.Apply(request, None)
    assert response.analyzeResults is not None


def test_when_allFields_is_true_return_all_fields():
    analyze_engine = AnalyzerEngine(
        registry=MockRecognizerRegistry(), nlp_engine=NlpEngineMock()
    )
    request = AnalyzeRequest()
    request.analyzeTemplate.allFields = True
    request.analyzeTemplate.resultsScoreThreshold = 0
    request.text = (
        " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090 "
        "Domain: microsoft.com"
    )
    response = analyze_engine.Apply(request, None)
    returned_entities = [field.field.name for field in response.analyzeResults]

    assert response.analyzeResults is not None
    assert "CREDIT_CARD" in returned_entities
    assert "PHONE_NUMBER" in returned_entities
    assert "DOMAIN_NAME" in returned_entities


def test_when_allFields_is_true_full_recognizers_list_return_all_fields(nlp_engine):
    analyze_engine = AnalyzerEngine(
        registry=RecognizerRegistry(), nlp_engine=nlp_engine
    )
    request = AnalyzeRequest()
    request.analyzeTemplate.allFields = True
    request.text = "My name is David and I live in Seattle." "Domain: microsoft.com "
    response = analyze_engine.Apply(request, None)
    returned_entities = [field.field.name for field in response.analyzeResults]
    assert response.analyzeResults is not None
    assert "PERSON" in returned_entities
    assert "LOCATION" in returned_entities
    assert "DOMAIN_NAME" in returned_entities


def test_when_allFields_is_true_and_entities_not_empty_exception():
    analyze_engine = AnalyzerEngine(
        registry=RecognizerRegistry(), nlp_engine=NlpEngineMock()
    )
    request = AnalyzeRequest()
    request.text = "My name is David and I live in Seattle." "Domain: microsoft.com "
    request.analyzeTemplate.allFields = True
    new_field = request.analyzeTemplate.fields.add()
    new_field.name = "CREDIT_CARD"
    new_field.minScore = "0.5"
    with pytest.raises(ValueError):
        analyze_engine.Apply(request, None)


def test_when_analyze_then_apptracer_has_value(
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
        all_fields=False,
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
        all_fields=False,
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
        all_fields=False,
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
        all_fields=False,
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
        all_fields=False,
    )

    assert len(results) == 2


@pytest.mark.slow
def test_demo_text(unit_test_guid, nlp_engine):
    text = (
        "Here are a few examples sentences we currently support:\n\n"
        "Hello, my name is David Johnson and I live in Maine.\n"
        "My credit card number is 4095-2609-9393-4932 and my "
        "Crypto wallet id is 16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ.\n\n"
        "On September 18 I visited microsoft.com and sent an "
        "email to test@microsoft.com,  from the IP 192.168.0.1.\n\n"
        "My passport: 991280345 and my phone number: (212) 555-1234.\n\n"
        "Please transfer using this IBAN IL150120690000003111111.\n\n"
        "Can you please check the status on bank account 954567876544 "
        "in PresidiBank?\n\n"
        ""
        "Kate's social security number is 078-05-1121.  "
        "Her driver license? it is 9234567B.\n\n"
        ""
        "This project welcomes contributions and suggestions.\n"
        "Most contributions require you to agree to a "
        "Contributor License Agreement (CLA) declaring "
        "that you have the right to, and actually do, "
        "grant us the rights to use your contribution. "
        "For details, visit https://cla.microsoft.com "
        "When you submit a pull request, "
        "a CLA-bot will automatically determine whether "
        "you need to provide a CLA and decorate the PR "
        "appropriately (e.g., label, comment).\n"
        "Simply follow the instructions provided by the bot. "
        "You will only need to do this once across all repos using our CLA.\n"
        "This project has adopted the Microsoft Open Source Code of Conduct.\n"
        "For more information see the Code of Conduct FAQ or "
        "contact opencode@microsoft.com with any additional questions or comments."
    )

    language = "en"

    analyzer_engine = AnalyzerEngine(
        default_score_threshold=0.35, nlp_engine=nlp_engine
    )
    results = analyzer_engine.analyze(
        correlation_id=unit_test_guid,
        text=text,
        entities=None,
        language=language,
        all_fields=True,
    )
    for result in results:
        text_slice = slice(result.start, result.end)
        logger.info(
            "Entity = {}, Text = {}, Score={}, Start={}, End={}".format(
                result.entity_type,
                text[text_slice],
                result.score,
                result.start,
                result.end,
            )
        )
    detected_entities = [result.entity_type for result in results]

    assert len([entity for entity in detected_entities if entity == "CREDIT_CARD"]) == 1
    assert len([entity for entity in detected_entities if entity == "CRYPTO"]) == 1
    assert len([entity for entity in detected_entities if entity == "DATE_TIME"]) == 1
    assert len([entity for entity in detected_entities if entity == "DOMAIN_NAME"]) == 4
    assert (
        len([entity for entity in detected_entities if entity == "EMAIL_ADDRESS"]) == 2
    )
    assert len([entity for entity in detected_entities if entity == "IBAN_CODE"]) == 1
    assert len([entity for entity in detected_entities if entity == "IP_ADDRESS"]) == 1
    assert len([entity for entity in detected_entities if entity == "LOCATION"]) == 1
    assert len([entity for entity in detected_entities if entity == "PERSON"]) == 2
    assert (
        len([entity for entity in detected_entities if entity == "PHONE_NUMBER"]) == 1
    )
    assert (
        len([entity for entity in detected_entities if entity == "US_BANK_NUMBER"]) == 1
    )
    assert (
        len([entity for entity in detected_entities if entity == "US_DRIVER_LICENSE"])
        == 1
    )
    assert len([entity for entity in detected_entities if entity == "US_PASSPORT"]) == 1
    assert len([entity for entity in detected_entities if entity == "US_SSN"]) == 1

    assert len(results) == 19


def test_get_recognizers_returns_predefined(nlp_engine):
    analyze_engine = AnalyzerEngine(
        registry=RecognizerRegistry(), nlp_engine=nlp_engine
    )
    request = RecognizersAllRequest(language="en")
    response = analyze_engine.GetAllRecognizers(request, None)
    # there are 15 predefined recognizers that detect the 17 entities
    assert len(response) == 15


def test_get_recognizers_returns_custom():
    pattern = Pattern("rocket pattern", r"\W*(rocket)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "ROCKET", name="Rocket recognizer", patterns=[pattern]
    )

    recognizers_store_api_mock = RecognizerStoreApiMock()
    recognizers_store_api_mock.add_custom_pattern_recognizer(pattern_recognizer)
    analyze_engine = AnalyzerEngine(
        registry=MockRecognizerRegistry(recognizers_store_api_mock),
        nlp_engine=NlpEngineMock(),
    )
    request = RecognizersAllRequest(language="en")
    response = analyze_engine.GetAllRecognizers(request, None)
    # there are 15 predefined recognizers and one custom
    assert len(response) == 16
    rocket_recognizer = [
        recognizer
        for recognizer in response
        if recognizer.name == "Rocket recognizer"
        and recognizer.entities == ["ROCKET"]
        and recognizer.language == "en"
    ]
    assert len(rocket_recognizer) == 1


def test_get_recognizers_returns_added_custom():
    pattern = Pattern("rocket pattern", r"\W*(rocket)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "ROCKET", name="Rocket recognizer", patterns=[pattern]
    )

    recognizers_store_api_mock = RecognizerStoreApiMock()

    analyze_engine = AnalyzerEngine(
        registry=MockRecognizerRegistry(recognizers_store_api_mock),
        nlp_engine=NlpEngineMock(),
    )
    request = RecognizersAllRequest(language="en")
    response = analyze_engine.GetAllRecognizers(request, None)
    # there are 15 predefined recognizers
    assert len(response) == 15
    recognizers_store_api_mock.add_custom_pattern_recognizer(pattern_recognizer)
    response = analyze_engine.GetAllRecognizers(request, None)
    # there are 15 predefined recognizers and one custom
    assert len(response) == 16


def test_get_recognizers_returns_supported_language():
    pattern = Pattern("rocket pattern", r"\W*(rocket)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "ROCKET",
        name="Rocket recognizer RU",
        patterns=[pattern],
        supported_language="ru",
    )

    recognizers_store_api_mock = RecognizerStoreApiMock()
    recognizers_store_api_mock.add_custom_pattern_recognizer(pattern_recognizer)
    analyze_engine = AnalyzerEngine(
        registry=MockRecognizerRegistry(recognizers_store_api_mock),
        nlp_engine=NlpEngineMock(),
    )
    request = RecognizersAllRequest(language="ru")
    response = analyze_engine.GetAllRecognizers(request, None)
    # there is only 1 mocked russian recognizer
    assert len(response) == 1
