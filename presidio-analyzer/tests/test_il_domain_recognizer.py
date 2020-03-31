from unittest import TestCase

from tests import assert_result
from presidio_analyzer.predefined_recognizers import ILDomainRecognizer
from presidio_analyzer.entity_recognizer import EntityRecognizer

domain_recognizer = ILDomainRecognizer()
entities = ["IL_DOMAIN_NAME"]


class TestILDomainRecognizer(TestCase):

    def test_invalid_domain(self):
        domain = 'קונטוסו.'
        results = domain_recognizer.analyze(domain, entities)

        assert len(results) == 0

    def test_invalid_domain_with_exact_context(self):
        domain = 'קונטוסו.'
        context = 'my domain is '
        results = domain_recognizer.analyze(context + domain, entities)

        assert len(results) == 0

    def test_valid_domain(self):
        domain = 'קונטוסו.co.il'
        results = domain_recognizer.analyze(domain, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 13, EntityRecognizer.MAX_SCORE)

    def test_full_valid_domain(self):
        domain = 'www.קונטוסו.co.il'
        results = domain_recognizer.analyze(domain, entities)

        assert_result(results[0], entities[0], 0, 17, EntityRecognizer.MAX_SCORE)

    def test_valid_domains_lemma_text(self):
        domain1 = 'קונטוסו.co.il'
        domain2 = 'קונטוסושלי.co.il'
        results = domain_recognizer.analyze('my domains: {} {}'.format(domain1, domain2), entities)

        assert len(results) == 2
        assert_result(results[0], entities[0], 12, 25, EntityRecognizer.MAX_SCORE)
        assert_result(results[1], entities[0], 26, 42, EntityRecognizer.MAX_SCORE)
