from unittest import TestCase
from analyzer.entity_recognizer import EntityRecognizer

import os
import hashlib
import pytest

from assertions import assert_result
from analyzer.analyze_pb2 import AnalyzeRequest

from analyzer import AnalyzerEngine, PatternRecognizer, Pattern, \
    RecognizerResult, RecognizerRegistry, AnalysisExplanation
from analyzer.predefined_recognizers import CreditCardRecognizer, \
    UsPhoneRecognizer, DomainRecognizer, UsItinRecognizer, \
    UsLicenseRecognizer, UsBankRecognizer, UsPassportRecognizer
from analyzer.recognizer_registry.recognizers_store_api \
    import RecognizerStoreApi  # noqa: F401
from analyzer.nlp_engine import SpacyNlpEngine, NlpArtifacts
from analyzer.predefined_recognizers import IpRecognizer, UsSsnRecognizer
from tests.mocks import MockNlpEngine
from tests.mocks.app_tracer_mock import AppTracerMock


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

    def add_custom_pattern_recognizer(self, new_recognizer,
                                      skip_hash_update=False):
        patterns = []
        for pat in new_recognizer.patterns:
            patterns.extend([Pattern(pat.name, pat.regex, pat.score)])
        new_custom_recognizer = PatternRecognizer(name=new_recognizer.name,
                                                  supported_entity=
                                                  new_recognizer.supported_entities[
                                                      0],
                                                  supported_language=new_recognizer.supported_language,
                                                  black_list=new_recognizer.black_list,
                                                  context=new_recognizer.context,
                                                  patterns=patterns)
        self.recognizers.append(new_custom_recognizer)

        if skip_hash_update:
            return

        m = hashlib.md5()
        for recognizer in self.recognizers:
            m.update(recognizer.name.encode('utf-8'))
        self.latest_hash = m.digest()

    def remove_recognizer(self, name):
        for i in self.recognizers:
            if i.name == name:
                self.recognizers.remove(i)

        m = hashlib.md5()
        for recognizer in self.recognizers:
            m.update(recognizer.name.encode('utf-8'))
        self.latest_hash = m.digest()


class MockRecognizerRegistry(RecognizerRegistry):
    """
    A mock that acts as a recognizers registry
    """

    def load_recognizers(self, path):
        #   TODO: Change the code to dynamic loading -
        # Task #598:  Support loading of the pre-defined recognizers
        # from the given path.
        self.recognizers.extend([CreditCardRecognizer(),
                                 UsPhoneRecognizer(),
                                 DomainRecognizer()])


loaded_spacy_nlp_engine = SpacyNlpEngine()


class TestAnalyzerEngine(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestAnalyzerEngine, self).__init__(*args, **kwargs)
        self.loaded_registry = MockRecognizerRegistry(RecognizerStoreApiMock())
        mock_nlp_artifacts = NlpArtifacts([], [], [], [], None, "en")
        self.app_tracer = AppTracerMock(enable_interpretability=True)
        self.loaded_analyzer_engine = AnalyzerEngine(self.loaded_registry,
                                                     MockNlpEngine(stopwords=[],
                                                                   punct_words=[],
                                                                   nlp_artifacts=mock_nlp_artifacts),
                                                     app_tracer=self.app_tracer,
                                                     enable_trace_pii=True)
        self.unit_test_guid = "00000000-0000-0000-0000-000000000000"

    def test_analyze_with_predefined_recognizers_return_results(self):
        text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
        language = "en"
        entities = ["CREDIT_CARD"]
        results = self.loaded_analyzer_engine.analyze(
            self.unit_test_guid,
            text, entities, language, all_fields=False)

        assert len(results) == 1
        assert_result(results[0], "CREDIT_CARD", 14,
                      33, EntityRecognizer.MAX_SCORE)

    def test_analyze_with_multiple_predefined_recognizers(self):
        text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
        language = "en"
        entities = ["CREDIT_CARD", "PHONE_NUMBER"]

        # This analyzer engine is different from the global one, as this one
        # also loads SpaCy so it can use the context words

        analyzer_engine_with_spacy = AnalyzerEngine(
            registry=self.loaded_registry, nlp_engine=loaded_spacy_nlp_engine)
        results = analyzer_engine_with_spacy.analyze(self.unit_test_guid, text,
                                                     entities, language,
                                                     all_fields=False)

        assert len(results) == 2
        assert_result(results[0], "CREDIT_CARD", 14,
                      33, EntityRecognizer.MAX_SCORE)
        expected_score = UsPhoneRecognizer.MEDIUM_REGEX_SCORE + \
                         PatternRecognizer.CONTEXT_SIMILARITY_FACTOR  # 0.5 + 0.35 = 0.85
        assert_result(results[1], "PHONE_NUMBER", 48, 59, expected_score)

    def test_analyze_without_entities(self):
        with pytest.raises(ValueError):
            language = "en"
            text = " Credit card: 4095-2609-9393-4932,  my name is  John Oliver, DateTime: September 18 Domain: microsoft.com"
            entities = []
            self.loaded_analyzer_engine.analyze(self.unit_test_guid,
                                                text, entities, language,
                                                all_fields=False)

    def test_analyze_with_empty_text(self):
        language = "en"
        text = ""
        entities = ["CREDIT_CARD", "PHONE_NUMBER"]
        results = self.loaded_analyzer_engine.analyze(self.unit_test_guid,
                                                      text, entities, language,
                                                      all_fields=False)

        assert len(results) == 0

    def test_analyze_with_unsupported_language(self):
        with pytest.raises(ValueError):
            language = "de"
            text = ""
            entities = ["CREDIT_CARD", "PHONE_NUMBER"]
            self.loaded_analyzer_engine.analyze(self.unit_test_guid,
                                                text, entities, language,
                                                all_fields=False)

    def test_remove_duplicates(self):
        # test same result with different score will return only the highest
        arr = [RecognizerResult(start=0, end=5, score=0.1, entity_type="x",
                                analysis_explanation=AnalysisExplanation(
                                    recognizer='test',
                                    original_score=0,
                                    pattern_name='test',
                                    pattern='test',
                                    validation_result=None)),
               RecognizerResult(start=0, end=5, score=0.5, entity_type="x",
                                analysis_explanation=AnalysisExplanation(
                                    recognizer='test',
                                    original_score=0,
                                    pattern_name='test',
                                    pattern='test',
                                    validation_result=None))]
        results = AnalyzerEngine._AnalyzerEngine__remove_duplicates(arr)
        assert len(results) == 1
        assert results[0].score == 0.5
        # TODO: add more cases with bug:
        # bug# 597: Analyzer remove duplicates doesn't handle all cases of one result as a substring of the other

    def test_remove_duplicates_different_entity_no_removal(self):
        # test same result with different score will return only the highest
        arr = [RecognizerResult(start=0, end=5, score=0.1, entity_type="x",
                                analysis_explanation=AnalysisExplanation(
                                    recognizer='test',
                                    original_score=0,
                                    pattern_name='test',
                                    pattern='test',
                                    validation_result=None)),
               RecognizerResult(start=0, end=5, score=0.5, entity_type="y",
                                analysis_explanation=AnalysisExplanation(
                                    recognizer='test',
                                    original_score=0,
                                    pattern_name='test',
                                    pattern='test',
                                    validation_result=None))]
        results = AnalyzerEngine._AnalyzerEngine__remove_duplicates(arr)
        assert len(results) == 2

    def test_added_pattern_recognizer_works(self):
        pattern = Pattern("rocket pattern", r'\W*(rocket)\W*', 0.8)
        pattern_recognizer = PatternRecognizer("ROCKET",
                                               name="Rocket recognizer",
                                               patterns=[pattern])

        # Make sure the analyzer doesn't get this entity
        recognizers_store_api_mock = RecognizerStoreApiMock()
        analyze_engine = AnalyzerEngine(registry=
        MockRecognizerRegistry(
            recognizers_store_api_mock),
            nlp_engine=MockNlpEngine())
        text = "rocket is my favorite transportation"
        entities = ["CREDIT_CARD", "ROCKET"]

        results = analyze_engine.analyze(self.unit_test_guid, text=text,
                                         entities=entities,
                                         language='en', all_fields=False)

        assert len(results) == 0

        # Add a new recognizer for the word "rocket" (case insensitive)
        recognizers_store_api_mock.add_custom_pattern_recognizer(
            pattern_recognizer)

        # Check that the entity is recognized:
        results = analyze_engine.analyze(self.unit_test_guid, text=text,
                                         entities=entities,
                                         language='en', all_fields=False)

        assert len(results) == 1
        assert_result(results[0], "ROCKET", 0, 7, 0.8)

    def test_removed_pattern_recognizer_doesnt_work(self):
        pattern = Pattern("spaceship pattern", r'\W*(spaceship)\W*', 0.8)
        pattern_recognizer = PatternRecognizer("SPACESHIP",
                                               name="Spaceship recognizer",
                                               patterns=[pattern])

        # Make sure the analyzer doesn't get this entity
        recognizers_store_api_mock = RecognizerStoreApiMock()
        analyze_engine = AnalyzerEngine(registry=MockRecognizerRegistry(
            recognizers_store_api_mock), nlp_engine=MockNlpEngine())
        text = "spaceship is my favorite transportation"
        entities = ["CREDIT_CARD", "SPACESHIP"]

        results = analyze_engine.analyze(self.unit_test_guid, text=text,
                                         entities=entities,
                                         language='en', all_fields=False)

        assert len(results) == 0

        # Add a new recognizer for the word "rocket" (case insensitive)
        recognizers_store_api_mock.add_custom_pattern_recognizer(
            pattern_recognizer)
        # Check that the entity is recognized:
        results = analyze_engine.analyze(self.unit_test_guid, text=text,
                                         entities=entities,
                                         language='en', all_fields=False)
        assert len(results) == 1
        assert_result(results[0], "SPACESHIP", 0, 10, 0.8)

        # Remove recognizer
        recognizers_store_api_mock.remove_recognizer(
            "Spaceship recognizer")
        # Test again to see we didn't get any results
        results = analyze_engine.analyze(self.unit_test_guid, text=text,
                                         entities=entities,
                                         language='en', all_fields=False)

        assert len(results) == 0

    def test_apply_with_language_returns_correct_response(self):
        request = AnalyzeRequest()
        request.analyzeTemplate.language = 'en'
        request.analyzeTemplate.resultsScoreThreshold = 0
        new_field = request.analyzeTemplate.fields.add()
        new_field.name = 'CREDIT_CARD'
        new_field.minScore = '0.5'
        request.text = "My credit card number is 4916994465041084"
        response = self.loaded_analyzer_engine.Apply(request, None)

        assert response.analyzeResults is not None

    def test_apply_with_no_language_returns_default(self):
        request = AnalyzeRequest()
        request.analyzeTemplate.language = ''
        request.analyzeTemplate.resultsScoreThreshold = 0
        new_field = request.analyzeTemplate.fields.add()
        new_field.name = 'CREDIT_CARD'
        new_field.minScore = '0.5'
        request.text = "My credit card number is 4916994465041084"
        response = self.loaded_analyzer_engine.Apply(request, None)
        assert response.analyzeResults is not None

    def test_when_allFields_is_true_return_all_fields(self):
        analyze_engine = AnalyzerEngine(registry=MockRecognizerRegistry(),
                                        nlp_engine=MockNlpEngine())
        request = AnalyzeRequest()
        request.analyzeTemplate.allFields = True
        request.analyzeTemplate.resultsScoreThreshold = 0
        request.text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090 " \
                       "Domain: microsoft.com"
        response = analyze_engine.Apply(request, None)
        returned_entities = [
            field.field.name for field in response.analyzeResults]

        assert response.analyzeResults is not None
        assert "CREDIT_CARD" in returned_entities
        assert "PHONE_NUMBER" in returned_entities
        assert "DOMAIN_NAME" in returned_entities

    def test_when_allFields_is_true_full_recognizers_list_return_all_fields(
            self):
        analyze_engine = AnalyzerEngine(registry=RecognizerRegistry(),
                                        nlp_engine=loaded_spacy_nlp_engine)
        request = AnalyzeRequest()
        request.analyzeTemplate.allFields = True
        request.text = "My name is David and I live in Seattle." \
                       "Domain: microsoft.com "
        response = analyze_engine.Apply(request, None)
        returned_entities = [
            field.field.name for field in response.analyzeResults]
        assert response.analyzeResults is not None
        assert "PERSON" in returned_entities
        assert "LOCATION" in returned_entities
        assert "DOMAIN_NAME" in returned_entities

    def test_when_allFields_is_true_and_entities_not_empty_exception(self):
        analyze_engine = AnalyzerEngine(registry=RecognizerRegistry(),
                                        nlp_engine=MockNlpEngine())
        request = AnalyzeRequest()
        request.text = "My name is David and I live in Seattle." \
                       "Domain: microsoft.com "
        request.analyzeTemplate.allFields = True
        new_field = request.analyzeTemplate.fields.add()
        new_field.name = 'CREDIT_CARD'
        new_field.minScore = '0.5'
        with pytest.raises(ValueError):
            analyze_engine.Apply(request, None)

    def test_when_analyze_then_apptracer_has_value(self):
        text = "My name is Bart Simpson, and Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
        language = "en"
        entities = ["CREDIT_CARD", "PHONE_NUMBER", "PERSON"]
        analyzer_engine_with_spacy = AnalyzerEngine(self.loaded_registry,
                                                    app_tracer=self.app_tracer,
                                                    enable_trace_pii=True)
        results = analyzer_engine_with_spacy.analyze(correlation_id=self.unit_test_guid,
                                                     text=text,
                                                     entities=entities,
                                                     language=language,
                                                     all_fields=False,
                                                     trace=True)
        assert len(results) == 3
        for result in results:
            assert result.analysis_explanation is not None
        assert self.app_tracer.get_msg_counter() == 2
        assert self.app_tracer.get_last_trace() is not None

    def test_when_threshold_is_zero_all_results_pass(self):
        text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
        language = "en"
        entities = ["CREDIT_CARD", "PHONE_NUMBER"]

        # This analyzer engine is different from the global one, as this one
        # also loads SpaCy so it can detect the phone number entity

        analyzer_engine = AnalyzerEngine(
            registry=self.loaded_registry, nlp_engine=MockNlpEngine())
        results = analyzer_engine.analyze(self.unit_test_guid, text,
                                          entities, language,
                                          all_fields=False,
                                          score_threshold=0)

        assert len(results) == 2

    def test_when_threshold_is_more_than_half_only_credit_card_passes(self):
        text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
        language = "en"
        entities = ["CREDIT_CARD", "PHONE_NUMBER"]

        # This analyzer engine is different from the global one, as this one
        # also loads SpaCy so it can detect the phone number entity

        analyzer_engine = AnalyzerEngine(
            registry=self.loaded_registry, nlp_engine=MockNlpEngine())
        results = analyzer_engine.analyze(self.unit_test_guid, text,
                                          entities, language,
                                          all_fields=False,
                                          score_threshold=0.51)

        assert len(results) == 1

    def test_when_default_threshold_is_more_than_half_only_one_passes(self):
        text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
        language = "en"
        entities = ["CREDIT_CARD", "PHONE_NUMBER"]

        # This analyzer engine is different from the global one, as this one
        # also loads SpaCy so it can detect the phone number entity

        analyzer_engine = AnalyzerEngine(
            registry=self.loaded_registry, nlp_engine=MockNlpEngine(),
            default_score_threshold=0.7)
        results = analyzer_engine.analyze(self.unit_test_guid, text,
                                          entities, language,
                                          all_fields=False)

        assert len(results) == 1

    def test_when_default_threshold_is_zero_all_results_pass(self):
        text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
        language = "en"
        entities = ["CREDIT_CARD", "PHONE_NUMBER"]

        # This analyzer engine is different from the global one, as this one
        # also loads SpaCy so it can detect the phone number entity

        analyzer_engine = AnalyzerEngine(
            registry=self.loaded_registry, nlp_engine=MockNlpEngine())
        results = analyzer_engine.analyze(self.unit_test_guid, text,
                                          entities, language,
                                          all_fields=False)

        assert len(results) == 2