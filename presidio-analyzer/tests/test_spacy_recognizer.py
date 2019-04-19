from unittest import TestCase

from assertions import assert_result, assert_result_within_score_range

from analyzer.nlp_engine import SpacyNlpEngine
from analyzer.predefined_recognizers import SpacyRecognizer
from analyzer.entity_recognizer import EntityRecognizer
from analyzer.nlp_engine import NlpArtifacts

NER_STRENGTH = 0.85
nlp_engine = SpacyNlpEngine()
spacy_recognizer = SpacyRecognizer()
entities = ["PERSON", "DATE_TIME"]


class TestSpacyRecognizer(TestCase):

    # Test Name Entity
    # Bug #617 : Spacy Recognizer doesn't recognize Dan as PERSON even though online spacy demo indicates that it does
    # See http://textanalysisonline.com/spacy-named-entity-recognition-ner
    # def test_person_first_name(self):
    #     name = 'Dan'
    #     results = spacy_recognizer.analyze(name, entities)

    #     assert len(results) == 1
    #     assert_result(results[0], entity[0], NER_STRENGTH)

    def test_person_first_name_with_context(self):
        name = 'Dan'
        context = 'my name is'
        text = '{} {}'.format(context, name)

        results = self.prepare_and_analyze(nlp_engine, text)
        assert len(results) == 1
        assert_result_within_score_range(
            results[0], entities[0], 11, 14, NER_STRENGTH, EntityRecognizer.MAX_SCORE)

    def test_person_full_name(self):
        text = 'Dan Tailor'
        results = self.prepare_and_analyze(nlp_engine, text)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 10, NER_STRENGTH)

    def test_person_full_name_with_context(self):
        name = 'John Oliver'
        context = ' is the funniest comedian'
        text = '{} {}'.format(name, context)
        results = self.prepare_and_analyze(nlp_engine, text)

        assert len(results) == 1
        assert_result_within_score_range(
            results[0], entities[0], 0, 11, NER_STRENGTH, EntityRecognizer.MAX_SCORE)

    def test_person_last_name(self):
        text = 'Tailor'
        results = self.prepare_and_analyze(nlp_engine, text)

        assert len(results) == 0

    # Bug #617 : Spacy Recognizer doesn't recognize Mr. Tailor as PERSON even though online spacy visualizer indicates that it does
    # See http://textanalysisonline.com/spacy-named-entity-recognition-ner
    # def test_person_title_with_last_name(self):
    #     name = 'Mr. Tailor'
    #     results = spacy_recognizer.analyze(name, entities)

    #     assert len(results) == 1
    #     assert_result(results[0], entities[0], 0, 9, NER_STRENGTH)

    # Bug #617 : Spacy Recognizer doesn't recognize Mr. Tailor as PERSON even though online spacy visualizer indicates that it does
    # See http://textanalysisonline.com/spacy-named-entity-recognition-ner
    # def test_person_title_with_last_name_with_context_and_time(self):
    #     name = 'Mr. Tailor'
    #     context = 'Good morning'
    #     results = spacy_recognizer.analyze('{} {}'.format(context, name), entities)

    #     assert len(results) == 2
    #     assert_result_within_score_range(results[1], entities[1], 5, 12, NER_STRENGTH, EntityRecognizer.MAX_SCORE)
    #     assert_result_within_score_range(results[0], entities[0], 17, 23, NER_STRENGTH, EntityRecognizer.MAX_SCORE)

    def test_person_full_middle_name(self):
        text = 'Richard Milhous Nixon'
        results = self.prepare_and_analyze(nlp_engine, text)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 21, NER_STRENGTH)

    def test_person_full_name_with_middle_letter(self):
        text = 'Richard M. Nixon'
        results = self.prepare_and_analyze(nlp_engine, text)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 16, NER_STRENGTH)

    def test_person_full_name_complex(self):
        text = 'Richard (Ric) C. Henderson'
        results = self.prepare_and_analyze(nlp_engine, text)

        assert len(results) == 3
        # Richard
        assert text[results[0].start:results[0].end] == "Richard"
        assert_result(results[0], entities[0], 0, 7, NER_STRENGTH)
        # Ric
        assert text[results[1].start:results[1].end] == "Ric"
        assert_result(results[1], entities[0], 9, 12, NER_STRENGTH)
        # C. Henderson
        assert text[results[2].start:results[2].end] == "C. Henderson"
        assert_result(results[2], entities[0], 14, 26, NER_STRENGTH)

    def test_person_last_name_is_also_a_date_with_context_expected_person_only(self):
        name = 'Dan May'
        context = "has a bank account"
        text = '{} {}'.format(name, context)
        results = self.prepare_and_analyze(nlp_engine, text)

        assert len(results) == 1
        print(results[0].score)
        print(results[0].entity_type)
        print(text[results[0].start:results[0].end])
        assert_result_within_score_range(
            results[0], entities[0], 0, 7, NER_STRENGTH, EntityRecognizer.MAX_SCORE)

    def test_person_title_and_last_name_is_also_a_date_expected_person_only(self):
        text = 'Mr. May'
        results = self.prepare_and_analyze(nlp_engine, text)

        assert len(results) == 1
        assert_result(results[0], entities[0], 4, 7, NER_STRENGTH)

    def test_person_title_and_last_name_is_also_a_date_with_context_expected_person_only(self):
        name = 'Mr. May'
        context = "They call me"
        text = '{} {}'.format(context, name)
        results = self.prepare_and_analyze(nlp_engine, text)
        assert len(results) == 1
        assert_result_within_score_range(results[0], entities[0], 17, 20, NER_STRENGTH, EntityRecognizer.MAX_SCORE)

# Test DATE_TIME Entity
    def test_date_time_year(self):
        text = '1972'
        results = self.prepare_and_analyze(nlp_engine, text)

        assert len(results) == 1
        assert_result(results[0], entities[1], 0, 4, NER_STRENGTH)

    def test_date_time_year_with_context(self):
        date = '1972'
        context = 'I bought my car in'
        text = '{} {}'.format(context, date)
        results = self.prepare_and_analyze(nlp_engine, text)

        assert len(results) == 1
        assert_result_within_score_range(
            results[0], entities[1], 19, 23, NER_STRENGTH, EntityRecognizer.MAX_SCORE)

    def test_date_time_month_with_context(self):
        date = 'May'
        context = 'I bought my car in'
        text = '{} {}'.format(context, date)
        results = self.prepare_and_analyze(nlp_engine, text)

        assert len(results) == 1
        assert_result_within_score_range(
            results[0], entities[1], 19, 22, NER_STRENGTH, EntityRecognizer.MAX_SCORE)

    def test_date_time_day_in_month(self):
        text = 'May 1st'
        results = self.prepare_and_analyze(nlp_engine, text)

        assert len(results) == 1
        assert_result_within_score_range(
            results[0], entities[1], 0, 7, NER_STRENGTH, EntityRecognizer.MAX_SCORE)

    def test_date_time_full_date(self):
        text = 'May 1st, 1977'
        results = self.prepare_and_analyze(nlp_engine, text)

        assert len(results) == 1
        assert_result_within_score_range(
            results[0], entities[1], 0, 13, NER_STRENGTH, EntityRecognizer.MAX_SCORE)

    def test_date_time_day_in_month_with_year_with_context(self):
        date = 'May 1st, 1977'
        context = 'I bought my car on'
        text = '{} {}'.format(context, date)
        results = self.prepare_and_analyze(nlp_engine, text)

        assert len(results) == 1
        assert_result_within_score_range(
            results[0], entities[1], 19, 32, NER_STRENGTH, EntityRecognizer.MAX_SCORE)

    def prepare_and_analyze(self, nlp, text):
        nlp_artifacts = nlp.process_text(text, "en")
        results = spacy_recognizer.analyze(
            text, entities, nlp_artifacts)
        return results
