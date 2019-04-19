from unittest import TestCase

from assertions import assert_result_within_score_range
from analyzer.predefined_recognizers import IpRecognizer

ip_recognizer = IpRecognizer()
entities = ["IP_ADDRESS"]


class TestIpRecognizer(TestCase):

    def test_valid_ipv4(self):
        ip = '192.168.0.1'
        context = 'microsoft.com '
        results = ip_recognizer.analyze(context + ip, entities)

        assert len(results) == 1
        assert_result_within_score_range(
            results[0], entities[0], 14, 25, 0.6, 0.81)

    def test_invalid_ipv4(self):
        ip = '192.168.0'
        context = 'my ip: '
        results = ip_recognizer.analyze(context + ip, entities)

        assert len(results) == 0

    '''
    TODO: fix ipv6 regex
    def test_valid_ipv6(self):
        ip = '684D:1111:222:3333:4444:5555:6:77'
        context = 'microsoft.com '
        results = ip_recognizer.analyze(context + ip, entities)
    
        assert len(results) == 1
        assert results[0].text == ip
        assert results[0].score > 0.59 and results[0].score < 0.8
    
    
    def test_valid_ipv6_with_exact_context(self):
        ip = '684D:1111:222:3333:4444:5555:6:77'
        context = 'my ip: '
        results = ip_recognizer.analyze(context + ip, entities)
    
        assert len(results) == 1
        assert results[0].text == ip
        assert results[0].score > 0.79 and results[0].score < 1
    '''

    def test_invalid_ipv6(self):
        ip = '684D:1111:222:3333:4444:5555:77'
        results = ip_recognizer.analyze('the ip is ' + ip, entities)

        assert len(results) == 0
