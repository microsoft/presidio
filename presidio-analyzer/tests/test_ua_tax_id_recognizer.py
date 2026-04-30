"""Tests for UaTaxIdRecognizer."""

import pytest
from presidio_analyzer.predefined_recognizers.country_specific.ukraine import (
    UaTaxIdRecognizer,
)


@pytest.fixture(scope="module")
def recognizer():
    return UaTaxIdRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["UA_TAX_ID"]


# Fictitious numbers with valid checksums (verified against the official algorithm).
VALID_TAX_IDS = [
    "1234567899",  # coefficients × [1..9] → weighted_sum=295 → check=9
    "1000000000",  # weighted_sum=-1 → -1%11=10 → 10%10=0
]

INVALID_TAX_IDS = [
    "1234567890",  # last digit 0, but algorithm gives 9
    "9999999999",  # last digit 9, verify mismatch
    "123456789",   # too short
    "12345678901", # too long
]


@pytest.mark.parametrize("tax_id", VALID_TAX_IDS)
def test_when_valid_ua_tax_id_then_validates(tax_id, recognizer):
    assert recognizer.validate_result(tax_id) is True


@pytest.mark.parametrize("tax_id", INVALID_TAX_IDS)
def test_when_invalid_ua_tax_id_then_invalidates(tax_id, recognizer):
    result = recognizer.validate_result(tax_id)
    assert result is False or result is None


def test_when_context_word_present_then_score_boosted(recognizer, entities):
    results = recognizer.analyze("РНОКПП 1234567899", entities, None)
    assert len(results) >= 1
    assert results[0].entity_type == "UA_TAX_ID"
