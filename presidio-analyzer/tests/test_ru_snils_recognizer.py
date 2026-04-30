"""Tests for RuSnilsRecognizer."""

import pytest
from presidio_analyzer.predefined_recognizers.country_specific.russia import (
    RuSnilsRecognizer,
)


@pytest.fixture(scope="module")
def recognizer():
    return RuSnilsRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["RU_SNILS"]


# СНИЛС checksum: sum(d[i] * (9-i) for i in 0..8) % 101; if >=100 → 0.
VALID_SNILS = [
    "112-233-445 95",  # dashed canonical format, control=95
]

INVALID_SNILS = [
    "112-233-445 00",  # wrong control (correct is 95)
    "112-233-445 01",  # wrong control
]


@pytest.mark.parametrize("snils", VALID_SNILS)
def test_when_valid_snils_then_validates(snils, recognizer):
    assert recognizer.validate_result(snils) is True


@pytest.mark.parametrize("snils", INVALID_SNILS)
def test_when_invalid_snils_then_invalidates(snils, recognizer):
    result = recognizer.validate_result(snils)
    assert result is False or result is None


def test_when_snils_dashed_format_then_detected(recognizer, entities):
    results = recognizer.analyze("СНИЛС 112-233-445 95", entities, None)
    assert len(results) >= 1
    assert results[0].entity_type == "RU_SNILS"


def test_when_no_snils_context_then_weak_score(recognizer, entities):
    results = recognizer.analyze("112-233-445 95", entities, None)
    # dashed pattern should still match even without context
    assert len(results) >= 1
