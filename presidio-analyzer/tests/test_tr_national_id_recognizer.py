"""Tests for Turkish National ID (TCKN) recognizer."""

import pytest
from presidio_analyzer.predefined_recognizers import TrNationalIdRecognizer

from tests import assert_result_within_score_range


@pytest.fixture(scope="module")
def recognizer():
    """Create a Turkish TCKN recognizer instance for testing."""
    return TrNationalIdRecognizer()


@pytest.fixture(scope="module")
def entities():
    """Return the Turkish TCKN entity type for testing."""
    return ["TR_NATIONAL_ID"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # Valid TCKNs with correct checksum
        ("10000000146", 1, ((0, 11),), ((0.5, 1.0),),),
        ("76543210794", 1, ((0, 11),), ((0.5, 1.0),),),
        ("36493665440", 1, ((0, 11),), ((0.5, 1.0),),),
        ("53857632436", 1, ((0, 11),), ((0.5, 1.0),),),
        ("94357219628", 1, ((0, 11),), ((0.5, 1.0),),),
        ("79059236630", 1, ((0, 11),), ((0.5, 1.0),),),
        ("64625294480", 1, ((0, 11),), ((0.5, 1.0),),),
        # Valid TCKNs in sentences
        (
            "TC Kimlik No: 10000000146",
            1,
            ((14, 25),),
            ((0.5, 1.0),),
        ),
        (
            "Başvuru sahibinin TCKN numarası 10000000146 olarak tescil edilmiştir.",
            1,
            ((32, 43),),
            ((0.5, 1.0),),
        ),
        # Multiple valid TCKNs
        (
            "Birinci kişi: 10000000146, ikinci kişi: 76543210794",
            2,
            ((14, 25), (40, 51),),
            ((0.5, 1.0), (0.5, 1.0),),
        ),
        # Invalid TCKNs - first digit is 0
        ("00000000000", 0, (), (),),
        ("02531814694", 0, (), (),),  # first digit 0, rest mathematically plausible
        # Invalid TCKNs - wrong 10th digit checksum
        ("12345678900", 0, (), (),),
        ("76543210780", 0, (), (),),
        ("83219500748", 0, (), (),),  # 10th digit wrong, single-digit mismatch
        ("11798724308", 0, (), (),),  # random entry, both 10th and 11th wrong
        # Invalid TCKNs - correct 10th digit but wrong 11th digit
        ("10000000145", 0, (), (),),
        ("62286775983", 0, (), (),),  # 10th correct, 11th wrong
        ("97485249605", 0, (), (),),  # OCR/typo scenario, single digit off
        # Invalid TCKNs - wrong length
        ("1234567890", 0, (), (),),
        ("123456789012", 0, (), (),),
        # Invalid TCKNs - non-digits
        ("abcdefghijk", 0, (), (),),
        # Context enhancement
        (
            "Turkish ID 10000000146",
            1,
            ((11, 22),),
            ((0.5, 1.0),),
        ),
        (
            "Türk kimlik numarası 36493665440",
            1,
            ((21, 32),),
            ((0.5, 1.0),),
        ),
    ],
)
def test_when_tckn_in_text_then_all_tckns_found(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
    max_score,
):
    """Test that Turkish TCKN recognizer correctly identifies TCKNs."""
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len

    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        if fn_score == "max":
            fn_score = max_score
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )


def test_validate_result_with_valid_tckn(recognizer):
    """Test validate_result method with valid TCKNs."""
    assert recognizer.validate_result("10000000146") is True
    assert recognizer.validate_result("76543210794") is True
    assert recognizer.validate_result("36493665440") is True
    assert recognizer.validate_result("53857632436") is True
    assert recognizer.validate_result("94357219628") is True
    assert recognizer.validate_result("79059236630") is True
    assert recognizer.validate_result("64625294480") is True


def test_validate_result_with_invalid_first_digit(recognizer):
    """Test validate_result method with TCKNs starting with 0."""
    assert recognizer.validate_result("00000000000") is False
    assert recognizer.validate_result("02531814694") is False


def test_validate_result_with_wrong_checksum(recognizer):
    """Test validate_result method with wrong checksum."""
    # 10th digit wrong
    assert recognizer.validate_result("12345678900") is False
    assert recognizer.validate_result("76543210780") is False
    assert recognizer.validate_result("83219500748") is False
    assert recognizer.validate_result("11798724308") is False
    # 10th digit correct but 11th digit wrong
    assert recognizer.validate_result("10000000145") is False
    assert recognizer.validate_result("62286775983") is False
    assert recognizer.validate_result("97485249605") is False


def test_validate_result_with_wrong_length(recognizer):
    """Test validate_result method with wrong length."""
    assert recognizer.validate_result("1234567890") is False
    assert recognizer.validate_result("123456789012") is False


def test_validate_result_with_non_digits(recognizer):
    """Test validate_result method with non-digit characters."""
    assert recognizer.validate_result("abcdefghijk") is False


def test_context_words(recognizer):
    """Test that context words are properly set."""
    expected_context = [
        "tc kimlik",
        "kimlik no",
        "kimlik numarası",
        "tckn",
        "tc no",
        "nüfus cüzdanı",
        "national id",
        "turkish id",
        "türk kimlik",
    ]
    assert recognizer.context == expected_context


def test_supported_entity(recognizer):
    """Test that supported entity is correctly set."""
    assert recognizer.supported_entities == ["TR_NATIONAL_ID"]


def test_supported_language(recognizer):
    """Test that supported language is correctly set."""
    assert recognizer.supported_language == "tr"
