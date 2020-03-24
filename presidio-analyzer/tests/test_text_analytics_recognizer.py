from unittest import TestCase

from presidio_analyzer import PresidioLogger
from tests import assert_result
from presidio_analyzer.predefined_recognizers.text_analytics_recognizer import TextAnalyticsRecognizer
from tests.mocks.text_analytics_dal_mock import TextAnalyticsDalMock

logger = PresidioLogger()

entities = ["DATE_TIME", "EMAIL_ADDRESS", "IP_ADDRESS", "PERSON", "PHONE_NUMBER", "LOCATION", "NRP"]


class TestEmailRecognizer(TestCase):

    def test_when_valid_entities_correct_analysis(self):
        recognizer = TextAnalyticsRecognizer(TextAnalyticsDalMock(
            '{"documents":[{"id":"0","entities":[{"text":"info@presidio.site","type":"Email","offset":12,'
            '"length":18,"score":0.8},{"text":"Bill Gates","type":"Person","offset":47,"length":10,"score":0.49},'
            '{"text":"Microsoft","type":"Organization","offset":72,"length":9,"score":0.99},{"text":"01/01/1970",'
            '"type":"DateTime","subtype":"Date","offset":98,"length":10,"score":0.8},{"text":"(312) 555-0176",'
            '"type":"PhoneNumber","offset":130,"length":14,"score":0.8},{"text":"10.0.0.101","type":"IP",'
            '"offset":159,"length":10,"score":0.8},{"text":"50.81425 4.4122","type":"EU GPS Coordinates",'
            '"offset":186,"length":15,"score":0.99}]}],"errors":[],"modelVersion":"2020-02-01"}'))

        text = 'My email is info@presidio.site, and my name is Bill Gates. He works for Microsoft.' \
               'His birthday is 01/01/1970. The phone number is (312) 555-0176, and pc ip is 10.0.0.101.' \
               'The location is 50.81425 4.4122'
        results = recognizer.analyze(text, entities)

        assert len(results) == 7
        assert_result(results[0], "EMAIL_ADDRESS", 12, 30, 0.8)
        assert_result(results[1], "PERSON", 47, 57, 0.49)
        assert_result(results[2], "NRP", 72, 81, 0.99)
        assert_result(results[3], "DATE_TIME", 98, 108, 0.8)
        assert_result(results[4], "PHONE_NUMBER", 130, 144, 0.8)
        assert_result(results[5], "IP_ADDRESS", 159, 169, 0.8)
        assert_result(results[6], "LOCATION", 186, 201, 0.99)

    def test_when_empty_text_no_response(self):
        recognizer = TextAnalyticsRecognizer(TextAnalyticsDalMock(
            '{"documents":[],"errors":[{"id":"0","error":{"code":"InvalidArgument","message":"Invalid document in '
            'request.","innerError":{"code":"InvalidDocument","message":"Document text is empty."}}}],'
            '"modelVersion":"2020-02-01"}'))
        text = ''
        results = recognizer.analyze(text, entities)

        assert len(results) == 0
