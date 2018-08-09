from analyzer import matcher
from tests import *
import datetime
import os

types = []

def test_all_fields_demo_file():
    start_time = datetime.datetime.now()
    path = os.path.dirname(__file__) + '/data/demo.txt'
    text_file = open(path, 'r')
    text = text_file.read()
    results = match.analyze_text(text, types)
    test_time = datetime.datetime.now() - start_time

    assert len(results) == 20
    assert test_time.seconds < 1
    assert test_time.microseconds < 800000
    print('test_all_fields_demo runtime: {} seconds, {} microseconds'.format(
        test_time.seconds, test_time.microseconds))


def test_all_fields_enron_file():
    start_time = datetime.datetime.now()
    path = os.path.dirname(__file__) + '/data/enron.txt'
    text_file = open(path, 'r')
    text = text_file.read()
    results = match.analyze_text(text, types)
    test_time = datetime.datetime.now() - start_time
    
    assert len(results) > 30
    assert test_time.seconds < 1
    assert test_time.microseconds < 800000
    print('test_all_fields_enron runtime: {} seconds, {} microseconds'.format(
        test_time.seconds, test_time.microseconds))
