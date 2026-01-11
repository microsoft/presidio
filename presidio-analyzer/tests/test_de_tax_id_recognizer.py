import pytest

from tests import assert_result, assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DeTaxIdRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeTaxIdRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_TAX_ID"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid Tax IDs (11 digits, first not 0, valid digit distribution, checksum valid)
        ("86095742719", 1, ((0, 11),), ((0.2, 1.0),)),
        ("11234567808", 1, ((0, 11),), ((0.2, 1.0),)),

        # With separators
        ("860 957 427 19", 1, ((0, 14),), ((0.3, 1.0),)),
        ("860-957-427-19", 1, ((0, 14),), ((0.3, 1.0),)),
        ("860/957/427/19", 1, ((0, 14),), ((0.3, 1.0),)),

        # With surrounding text
        ("My Tax ID is 86095742719 here", 1, ((13, 24),), ((0.2, 1.0),)),
        ("Steuer-ID: 860 957 427 19", 1, ((11, 25),), ((0.3, 1.0),)),

        # Multiple Tax IDs
        ("IDs: 86095742719 and 11234567808", 2, ((5, 16), (21, 32)), ((0.2, 1.0), (0.2, 1.0))),

        # Invalid - first digit is 0
        ("01234567890", 0, (), ()),

        # Invalid - wrong length
        ("8609574271", 0, (), ()),
        ("860957427190", 0, (), ()),

        # Invalid - contains letters
        ("8609574271A", 0, (), ()),
        # fmt: on
    ],
)
def test_when_tax_id_in_text_then_all_ids_found(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )


@pytest.mark.parametrize(
    "text, expected",
    [
        # Valid Tax ID with correct checksum and digit distribution
        ("86095742719", True),
        ("11234567808", True),
        # Invalid - first digit is 0
        ("01234567890", False),
        # Invalid - wrong length
        ("8609574271", False),
        # Invalid - all same digits (violates distribution rule)
        ("11111111111", False),
        # Invalid - checksum wrong
        ("12345678903", False),
    ],
)
def test_validate_result(text, expected, recognizer):
    """Test the validate_result method directly."""
    result = recognizer.validate_result(text)
    assert result == expected


def test_digit_distribution_validation(recognizer):
    """Test that digit distribution is properly validated."""
    # Valid: one digit appears 2 or 3 times, at least one digit missing
    assert recognizer._validate_digit_distribution("8609574271") is True
    assert recognizer._validate_digit_distribution("1123456780") is True  # 1 appears twice, 9 missing

    # Invalid: all 10 different digits (no digit appears twice)
    assert recognizer._validate_digit_distribution("1234567890") is False


def test_checksum_validation(recognizer):
    """Test the ISO 7064 MOD 11,10 checksum validation."""
    # Valid checksum
    assert recognizer._validate_checksum("86095742719") is True


def test_recognizer_initialization():
    """Test recognizer initialization with default parameters."""
    recognizer = DeTaxIdRecognizer()
    assert recognizer.supported_entities == ["DE_TAX_ID"]
    assert recognizer.supported_language == "de"
    assert len(recognizer.patterns) == 2
    assert len(recognizer.context) > 0
