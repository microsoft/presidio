import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DeSocialSecurityRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeSocialSecurityRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_SOCIAL_SECURITY"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid format: BBTTMMJJASSP (area, day, month, year, letter, serial, check)
        # Area codes 02-89 are valid, day 01-31, month 01-12
        # Checksums calculated per official VKVV § 2 weights: 2,1,2,5,7,1,2,1,2,1,2,1
        ("12150485M004", 1, ((0, 12),), ((0.25, 1.0),)),
        ("65170590A003", 1, ((0, 12),), ((0.25, 1.0),)),
        ("38010175Z998", 1, ((0, 12),), ((0.25, 1.0),)),

        # With spaces
        ("12 150485 M 12", 0, (), ()),  # Spaces in wrong positions

        # With surrounding text
        ("My SVNR is 12150485M004 here", 1, ((11, 23),), ((0.25, 1.0),)),
        ("Sozialversicherungsnummer: 65170590A003", 1, ((27, 39),), ((0.25, 1.0),)),

        # Multiple SSNs
        ("Numbers: 12150485M004 and 65170590A003", 2, ((9, 21), (26, 38)), ((0.25, 1.0), (0.25, 1.0))),

        # Invalid - wrong area code (01 is not valid)
        ("01150485M123", 0, (), ()),

        # Invalid - wrong day (32 is not valid)
        ("12320485M123", 0, (), ()),

        # Invalid - wrong month (13 is not valid)
        ("12151385M123", 0, (), ()),

        # Invalid - wrong length
        ("12150485M12", 0, (), ()),
        ("12150485M1234", 0, (), ()),

        # Invalid - no letter in position 8
        ("12150485123", 0, (), ()),
        # fmt: on
    ],
)
def test_when_social_security_in_text_then_all_found(
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
        # Valid format with valid checksum (per VKVV § 2)
        ("12150485M004", True),
        ("65170590A003", True),
        ("38010175Z998", True),
        # Invalid - wrong checksum
        ("12150485M008", False),
        # Invalid - wrong area code
        ("01150485M004", False),
        # Invalid - wrong day
        ("12320485M004", False),
        # Invalid - wrong month
        ("12151385M004", False),
        # Invalid - wrong length
        ("12150485M12", False),
    ],
)
def test_validate_result(text, expected, recognizer):
    """Test the validate_result method directly."""
    result = recognizer.validate_result(text)
    assert result == expected


def test_valid_area_codes(recognizer):
    """Test that valid area codes are accepted."""
    valid_codes = ["02", "10", "38", "50", "65", "80"]
    for code in valid_codes:
        assert code in recognizer.VALID_AREA_CODES


def test_invalid_area_codes(recognizer):
    """Test that invalid area codes are rejected."""
    invalid_codes = ["00", "01", "30", "31", "32", "33", "34", "35", "36", "37", "41", "90", "99"]
    for code in invalid_codes:
        assert code not in recognizer.VALID_AREA_CODES


def test_recognizer_initialization():
    """Test recognizer initialization with default parameters."""
    recognizer = DeSocialSecurityRecognizer()
    assert recognizer.supported_entities == ["DE_SOCIAL_SECURITY"]
    assert recognizer.supported_language == "de"
    assert len(recognizer.patterns) == 2
    assert len(recognizer.context) > 0
