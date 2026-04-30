"""Tests for UaPassportRecognizer."""

import pytest
from presidio_analyzer import RecognizerResult
from presidio_analyzer.predefined_recognizers.country_specific.ukraine import (
    UaPassportRecognizer,
)


@pytest.fixture(scope="module")
def recognizer():
    return UaPassportRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["UA_PASSPORT"]


@pytest.mark.parametrize(
    "text,expected_count",
    [
        ("Серія паспорта АА 123456", 1),      # old Cyrillic format with space
        ("паспорт КВ123456", 1),               # old Cyrillic format no space
        ("passport AA 123456 biometric", 1),   # biometric MRZ format
        ("номер AA123456", 1),                 # biometric MRZ no space
        ("no numbers here", 0),
    ],
)
def test_when_text_contains_ua_passport_then_detected(
    text, expected_count, recognizer, entities
):
    results = recognizer.analyze(text, entities, None)
    assert len(results) == expected_count


@pytest.mark.parametrize(
    "text",
    [
        "паспорт АА 123456",
        "паспорт КВ654321",
    ],
)
def test_when_ua_passport_context_present_then_result_returned(text, recognizer, entities):
    results = recognizer.analyze(text, entities, None)
    assert len(results) >= 1
    assert results[0].entity_type == "UA_PASSPORT"
