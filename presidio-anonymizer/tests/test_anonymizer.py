import unittest
from anonymizer import app


class TestAnonymizer(unittest.TestCase):
    def test_anonymize(self):
        tester = app.test_client(self)
        resp = tester.post('/anonymize', json={'hello': 1, 'world':'what?'})
        assert resp.json == {'hello': 1, 'world':'what?'}
