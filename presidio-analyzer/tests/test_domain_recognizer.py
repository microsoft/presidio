from unittest import TestCase

from assertions import assert_result
from analyzer.predefined_recognizers import DomainRecognizer
from analyzer.entity_recognizer import EntityRecognizer

domain_recognizer = DomainRecognizer()
entities = ["DOMAIN_NAME"]


class TestDomainRecognizer(TestCase):

    def test_invalid_domain(self):
        domain = 'microsoft.'
        results = domain_recognizer.analyze(domain, entities)

        assert len(results) == 0


    def test_invalid_domain_with_exact_context(self):
        domain = 'microsoft.'
        context = 'my domain is '
        results = domain_recognizer.analyze(context + domain, entities)

        assert len(results) == 0


    def test_valid_domain(self):
        domain = 'microsoft.com'
        results = domain_recognizer.analyze(domain, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 13, EntityRecognizer.MAX_SCORE)

    def test_valid_domains_lemma_text(self):
        domain1 = 'microsoft.com'
        domain2 = 'google.co.il' 
        results = domain_recognizer.analyze('my domains: {} {}'.format(domain1, domain2), entities)

        assert len(results) == 2
        assert_result(results[0], entities[0], 12, 25, EntityRecognizer.MAX_SCORE)
        assert_result(results[1], entities[0], 26, 38, EntityRecognizer.MAX_SCORE)
