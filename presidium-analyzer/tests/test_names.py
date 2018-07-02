from analyzer import matcher
import logging

import os

types = ["PERSON"]


def test_person_name_simple():
    match = matcher.Matcher()

    name = 'John Oliver'
    results = match.analyze_text(name + " is the funniest comedian", types)

    assert results[0].value == name
