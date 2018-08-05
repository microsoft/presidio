from analyzer import matcher
from tests import *
import datetime
import os

types = []


def test_all_fields_from_file():
    start_time = datetime.datetime.now()
    path = os.path.dirname(__file__) + '/data/demo.txt'
    text_file = open(path, 'r')
    text = text_file.read()
    results = match.analyze_text(text, types)
    test_time = datetime.datetime.now() - start_time

    assert len(results) == 6
    assert test_time.seconds < 1
    print('test_all_fields runtime: {} seconds, {} microseconds'.format(
        test_time.seconds, test_time.microseconds))
