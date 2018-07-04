from analyzer import matcher
import logging

import os

types = ["DATE_TIME"]


def test_date_time_simple():
    match = matcher.Matcher()

    name = 'May 1st'
    results = match.analyze_text(name + " is the workers holiday", types)

    assert results[0].text == name
