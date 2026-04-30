"""Tests for RuInnRecognizer."""

import pytest
from presidio_analyzer.predefined_recognizers.country_specific.russia import (
    RuInnRecognizer,
)


@pytest.fixture(scope="module")
def recognizer():
    return RuInnRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["RU_TAX_ID"]


# Valid INN values from ФНС test vectors and public sources.
VALID_ORG_INNS = [
    "7707083893",   # Сбербанк России
    "7736050003",   # Газпром
]

VALID_IND_INNS = [
    "500100732259",  # fictitious with valid checksum
]

INVALID_INNS = [
    "1234567890",    # wrong check digit (org)
    "123456789012",  # wrong check digit (individual)
    "12345",         # wrong length
]


@pytest.mark.parametrize("inn", VALID_ORG_INNS)
def test_when_valid_org_inn_then_validates(inn, recognizer):
    assert recognizer.validate_result(inn) is True


@pytest.mark.parametrize("inn", INVALID_INNS)
def test_when_invalid_inn_then_invalidates(inn, recognizer):
    result = recognizer.validate_result(inn)
    assert result is False or result is None


def test_when_inn_context_present_then_entity_detected(recognizer, entities):
    results = recognizer.analyze("ИНН 7707083893", entities, None)
    assert len(results) >= 1
    assert results[0].entity_type == "RU_TAX_ID"
