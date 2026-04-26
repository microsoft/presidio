"""Tests for Turkish phone number (TR_PHONE_NUMBER) recognizer."""

import pytest
from presidio_analyzer.predefined_recognizers import TrPhoneNumberRecognizer

from tests import assert_result_within_score_range


@pytest.fixture(scope="module")
def recognizer():
    """Create a TrPhoneNumberRecognizer instance for testing."""
    return TrPhoneNumberRecognizer()


@pytest.fixture(scope="module")
def entities():
    """Return the TR_PHONE_NUMBER entity type for testing."""
    return ["TR_PHONE_NUMBER"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # International format (+90)
        ("+905321234567", 1, ((0, 13),), ((0.4, 1.0),)),
        ("+90 532 123 45 67", 1, ((0, 17),), ((0.4, 1.0),)),
        ("+90-532-123-45-67", 1, ((0, 17),), ((0.4, 1.0),)),
        ("+90 (532) 123 45 67", 1, ((0, 19),), ((0.4, 1.0),)),
        # National format (0)
        ("05321234567", 1, ((0, 11),), ((0.3, 1.0),)),
        ("0 532 123 45 67", 1, ((0, 15),), ((0.3, 1.0),)),
        ("0-532-123-45-67", 1, ((0, 15),), ((0.3, 1.0),)),
        ("0 (532) 1234567", 1, ((0, 15),), ((0.3, 1.0),)),
        # Local format (just the number)
        ("5321234567", 1, ((0, 10),), ((0.15, 1.0),)),
        ("532 123 45 67", 1, ((0, 13),), ((0.15, 1.0),)),
        ("532-123-45-67", 1, ((0, 13),), ((0.15, 1.0),)),
        # In sentence with context
        (
            "Telefon numaram +905321234567 olarak kayıtlı.",
            1,
            ((16, 29),),
            ((0.4, 1.0),),
        ),
        (
            "Cep no: 05321234567",
            1,
            ((8, 19),),
            ((0.3, 1.0),),
        ),
        (
            "Phone: 5321234567",
            1,
            ((7, 17),),
            ((0.15, 1.0),),
        ),
        # Multiple numbers
        (
            "Birinci: +905321234567, İkinci: 05359876543",
            2,
            ((9, 22), (32, 43)),
            ((0.4, 1.0), (0.3, 1.0)),
        ),
        # Geographic number: starts with 4 (valid geographic)
        ("4321234567", 1, ((0, 10),), ((0.05, 1.0),)),
        # Invalid: too short
        ("532123456", 0, (), ()),
        # Invalid: too long (11 digits without prefix)
        ("53212345678", 0, (), ()),
        # Invalid: not a phone number
        ("hello world", 0, (), ()),
        ("1234567890", 0, (), ()),
        # False positive: random 10-digit number not starting with 5
        ("12345678901", 0, (), ()),
        # Geographic numbers: valid area codes (starts with 2, 3, 4)
        ("2121234567", 1, ((0, 10),), ((0.05, 1.0),)),
        ("3121234567", 1, ((0, 10),), ((0.05, 1.0),)),
        ("4621234567", 1, ((0, 10),), ((0.05, 1.0),)),
        # Geographic numbers (lower priority)
        ("02121234567", 1, ((0, 11),), ((0.1, 1.0),)),
        ("0216 123 45 67", 1, ((0, 14),), ((0.1, 1.0),)),
        ("0232 123 45 67", 1, ((0, 14),), ((0.05, 1.0),)),
        ("0312 123 45 67", 1, ((0, 14),), ((0.1, 1.0),)),
        ("0412 123 45 67", 1, ((0, 14),), ((0.1, 1.0),)),

        # False positive: embedded in longer number
        ("15053212345678", 0, (), ()),
        # Geographic number: starts with 2 (valid geographic)
        ("2023123456", 1, ((0, 10),), ((0.05, 1.0),)),
        # False positive: TCKN-like (11 digits starting with 1)
        ("10000000146", 0, (), ()),
        # False positive: IP address fragment
        ("532.123.45.67", 0, (), ()),
        # False positive: Turkish plate-like
        ("34 ABC 1234", 0, (), ()),
        # Invalid: unused first digits in Turkey (1, 6, 7, 8, 9)
        ("1123456789", 0, (), ()),
        ("6123456789", 0, (), ()),
        ("7123456789", 0, (), ()),
        ("8123456789", 0, (), ()),
        ("9123456789", 0, (), ()),
    ],
)
def test_when_phone_in_text_then_all_phones_found(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
):
    """Test that Turkish phone number recognizer correctly identifies numbers."""
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len

    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )


def test_validate_result_with_international_format(recognizer):
    """Test validate_result with international format (+90)."""
    assert recognizer.validate_result("+905321234567") is True
    assert recognizer.validate_result("+90 532 123 45 67") is True
    assert recognizer.validate_result("+90-532-123-45-67") is True


def test_validate_result_with_national_format(recognizer):
    """Test validate_result with national format (0)."""
    assert recognizer.validate_result("05321234567") is True
    assert recognizer.validate_result("0 532 123 45 67") is True
    assert recognizer.validate_result("0-532-123-45-67") is True


def test_validate_result_with_local_format(recognizer):
    """Test validate_result with local format."""
    assert recognizer.validate_result("5321234567") is True
    assert recognizer.validate_result("532 123 45 67") is True
    assert recognizer.validate_result("532-123-45-67") is True


def test_validate_result_with_invalid_prefix(recognizer):
    """Test validate_result with non-mobile prefix."""
    # These are now valid geographic numbers (4 prefix)
    assert recognizer.validate_result("+904321234567") is True  # Geographic
    assert recognizer.validate_result("04321234567") is True    # Geographic
    assert recognizer.validate_result("4321234567") is True     # Geographic


def test_validate_result_with_wrong_length(recognizer):
    """Test validate_result with wrong length."""
    assert recognizer.validate_result("532123456") is False
    assert recognizer.validate_result("53212345678") is False


def test_validate_result_with_geographic_numbers(recognizer):
    """Test validate_result with geographic numbers."""
    # Istanbul area codes
    assert recognizer.validate_result("02121234567") is True
    assert recognizer.validate_result("0216 123 45 67") is True

    # İzmir area code
    assert recognizer.validate_result("02321234567") is True

    # Ankara area code
    assert recognizer.validate_result("03121234567") is True

    # Antalya area code
    assert recognizer.validate_result("02421234567") is True


def test_validate_result_with_invalid_first_digit(recognizer):
    """Test validate_result with invalid first digit."""
    # Invalid first digits (1, 6, 7, 8, 9 are not used in Turkey)
    assert recognizer.validate_result("1123456789") is False
    assert recognizer.validate_result("6123456789") is False
    assert recognizer.validate_result("7123456789") is False
    assert recognizer.validate_result("8123456789") is False
    assert recognizer.validate_result("9123456789") is False


def test_validate_result_with_empty_input(recognizer):
    """Test validate_result with empty input."""
    assert recognizer.validate_result("") is None


def test_validate_result_with_non_digits(recognizer):
    """Test validate_result with non-digit characters."""
    assert recognizer.validate_result("abcdefghijk") is None


def test_context_words(recognizer):
    """Test that context words are properly set."""
    assert "telefon" in recognizer.context
    assert "cep telefonu" in recognizer.context
    assert "phone" in recognizer.context
    assert "mobile" in recognizer.context


def test_supported_entity(recognizer):
    """Test that supported entity is correctly set."""
    assert recognizer.supported_entities == ["TR_PHONE_NUMBER"]


def test_supported_language(recognizer):
    """Test that supported language is correctly set."""
    assert recognizer.supported_language == "tr"
