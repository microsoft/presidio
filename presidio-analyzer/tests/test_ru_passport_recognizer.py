"""Tests for RuPassportRecognizer."""

import pytest
from presidio_analyzer.predefined_recognizers.country_specific.russia import (
    RuPassportRecognizer,
)


@pytest.fixture(scope="module")
def recognizer():
    return RuPassportRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["RU_PASSPORT"]


@pytest.mark.parametrize(
    "text,expected_count",
    [
        ("паспорт 45 10 123456", 1),    # full spaced format
        ("серия: 4510 123456", 1),       # series/number with single space
        ("паспорт 4510123456", 1),       # no separator
        ("no numbers here", 0),
    ],
)
def test_when_text_contains_ru_passport_then_detected(
    text, expected_count, recognizer, entities
):
    results = recognizer.analyze(text, entities, None)
    assert len(results) == expected_count


def test_when_ru_passport_context_present_then_entity_type_correct(recognizer, entities):
    results = recognizer.analyze("паспорт гражданина 45 10 123456", entities, None)
    assert any(r.entity_type == "RU_PASSPORT" for r in results)
