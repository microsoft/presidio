from analyzer import matcher
import os

types = []


def test_all_fields_from_file():
    match = matcher.Matcher()
    path = os.path.dirname(__file__) + '/data/demo.txt'
    text_file = open(path, 'r')
    text = text_file.read()
    results = match.analyze_text(text, types)
    assert len(results) == 8
