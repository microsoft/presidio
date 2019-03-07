from unittest import TestCase

from assertions import assert_result
from analyzer.predefined_recognizers import EmailRecognizer
from analyzer.entity_recognizer import EntityRecognizer

email_recognizer = EmailRecognizer()
entities = ["EMAIL_ADDRESS"]


class TestEmailRecognizer(TestCase):

    def test_valid_email_no_context(self):
        email = 'info@presidio.site'
        results = email_recognizer.analyze(email, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 18, EntityRecognizer.MAX_SCORE)

    def test_valid_email_with_context(self):
        email = 'info@presidio.site'
        results = email_recognizer.analyze('my email is {}'.format(email), entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 12, 30, EntityRecognizer.MAX_SCORE)

    def test_multiple_emails_with_lemma_context(self):
        email1 = 'info@presidio.site'
        email2 = 'anotherinfo@presidio.site'
        results = email_recognizer.analyze(
            'try one of this emails: {} or {}'.format(email1, email2), entities)

        assert len(results) == 2
        assert_result(results[0], entities[0], 24, 42, EntityRecognizer.MAX_SCORE)
        assert_result(results[1], entities[0], 46, 71, EntityRecognizer.MAX_SCORE)

    def test_invalid_email(self):
        email = 'my email is info@presidio.'
        results = email_recognizer.analyze('the email is ' + email, entities)

        assert len(results) == 0
