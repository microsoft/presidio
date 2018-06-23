from analyzer import matcher
import logging
import os

# https://www.datatrans.ch/showcase/test-cc-numbers

types = ["CREDIT_CARD"]


def test_valid_credit_card():
    match = matcher.Matcher()

    number = '4012888888881881 4012-8888-8888-1881 4012 8888 8888 1881'
    results = match.analyze_text('my credit card number is ' + number, types)

    assert len(results) == 3


def test_invalid_credit_card():
    match = matcher.Matcher()

    number = '4012-8888-8888-1882'
    results = match.analyze_text('my credit card number is ' + number, types)

    assert len(results) == 0


def test_credit_card_text1():
    path = os.path.dirname(__file__) + '/data/text1.txt'
    text_file = open(path, 'r')
    match = matcher.Matcher()
    results = match.analyze_text(text_file.read(), types)
    assert len(results) == 3
