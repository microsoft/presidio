"""Tests for Turkish license plate (TR_LICENSE_PLATE) recognizer."""

import pytest
from presidio_analyzer.predefined_recognizers import TrLicensePlateRecognizer

from tests import assert_result_within_score_range


@pytest.fixture(scope="module")
def recognizer():
    """Create a TrLicensePlateRecognizer instance for testing."""
    return TrLicensePlateRecognizer()


@pytest.fixture(scope="module")
def entities():
    """Return the TR_LICENSE_PLATE entity type for testing."""
    return ["TR_LICENSE_PLATE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        ("34 ABC 1234", 1, ((0, 11),), ((0.5, 1.0),)),
        ("06 A 123", 1, ((0, 8),), ((0.5, 1.0),)),
        ("35 JK 12", 1, ((0, 8),), ((0.5, 1.0),)),
        ("16 B 1234", 1, ((0, 9),), ((0.5, 1.0),)),
        ("34ABC1234", 1, ((0, 9),), ((0.5, 1.0),)),
        ("34 abc 1234", 1, ((0, 11),), ((0.5, 1.0),)),
        (
            "Araç plakası 34 ABC 1234 olarak kayıtlıdır.",
            1,
            ((13, 24),),
            ((0.5, 1.0),),
        ),
        (
            "Plaka 34 ABC 1234 ve 06 JK 567",
            2,
            ((6, 17), (21, 30)),
            ((0.5, 1.0), (0.5, 1.0)),
        ),
        ("01 A 12", 1, ((0, 7),), ((0.5, 1.0),)),
        ("81 A 12", 1, ((0, 7),), ((0.5, 1.0),)),
        ("07 AB 123", 1, ((0, 9),), ((0.5, 1.0),)),
        ("00 ABC 123", 0, (), ()),
        ("82 ABC 123", 0, (), ()),
        ("99 ABC 123", 0, (), ()),
        ("hello world", 0, (), ()),
        ("1234567890", 0, (), ()),
        (
            "License plate 34 ABC 1234",
            1,
            ((14, 25),),
            ((0.5, 1.0),),
        ),
        (
            "Plaka numarası 06 A 123 olarak kayıtlı",
            1,
            ((15, 23),),
            ((0.5, 1.0),),
        ),
    ],
)
def test_when_license_plate_in_text_then_all_plates_found(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
):
    """Test that Turkish license plate recognizer correctly identifies plates."""
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len

    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )


def test_validate_result_with_valid_province(recognizer):
    """Test validate_result with valid province codes."""
    assert recognizer.validate_result("34 ABC 1234") is True
    assert recognizer.validate_result("06 A 123") is True
    assert recognizer.validate_result("01 A 12") is True
    assert recognizer.validate_result("81 A 12") is True


def test_validate_result_with_invalid_province(recognizer):
    """Test validate_result with invalid province codes."""
    assert recognizer.validate_result("00 ABC 123") is False
    assert recognizer.validate_result("82 ABC 123") is False


def test_validate_result_with_short_input(recognizer):
    """Test validate_result with input shorter than 3 characters."""
    assert recognizer.validate_result("12") is None
    assert recognizer.validate_result("") is None


def test_validate_result_with_non_numeric_province(recognizer):
    """Test validate_result when province code is not numeric."""
    assert recognizer.validate_result("AB ABC 123") is None
    assert recognizer.validate_result("XY 123") is None


def test_context_words(recognizer):
    """Test that context words are properly set."""
    assert "plaka" in recognizer.context
    assert "araç plakası" in recognizer.context
    assert "license plate" in recognizer.context


def test_supported_entity(recognizer):
    """Test that supported entity is correctly set."""
    assert recognizer.supported_entities == ["TR_LICENSE_PLATE"]


def test_supported_language(recognizer):
    """Test that supported language is correctly set."""
    assert recognizer.supported_language == "tr"
