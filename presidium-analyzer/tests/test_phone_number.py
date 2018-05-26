from analyzer import matcher
import logging
import os

types = ["PHONE_NUMBER"]


def test_phone_number_simple():
    match = matcher.Matcher()
    number = '052-5552606'
    results = match.analyze_text('my phone number is ' + number, types)

    assert results[0].value == number


def test_phone_number_text1():
    path = os.getcwd() + '/tests/data/text1.txt'
    text_file = open(path, 'r')
    match = matcher.Matcher()
    results = match.analyze_text(text_file.read(), types)
    assert (len(results) == 1)
