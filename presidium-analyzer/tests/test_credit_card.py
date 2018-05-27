from analyzer import matcher
import logging
import os

# https://www.datatrans.ch/showcase/test-cc-numbers

types = ["CREDIT_CARD"]


def test_credit_card_simple():
    match = matcher.Matcher()
    number = '4012-8888-8888-1881'
    results = match.analyze_text('my credit card number is ' + number, types)

    assert results[0].value == number


def test_credit_card_text1():
    path = os.getcwd() + '/tests/data/text1.txt'
    text_file = open(path, 'r')
    match = matcher.Matcher()
    results = match.analyze_text(text_file.read(), types)
    assert (len(results) == 3)
    assert (results[1].probability == 1)
