import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DeLicensePlateRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeLicensePlateRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_LICENSE_PLATE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid hyphen format (district-letters digits)
        ("B-AB 1234", 1, ((0, 9),), ((0.5, 1.0),)),
        ("M-XY 123", 1, ((0, 8),), ((0.5, 1.0),)),

        # Valid space format (district letters digits) - score 0.4
        ("B AB 1234", 1, ((0, 9),), ((0.3, 1.0),)),
        ("DD MC 5678", 1, ((0, 10),), ((0.3, 1.0),)),
        ("HH ZB 999", 1, ((0, 9),), ((0.3, 1.0),)),

        # Valid continuous format (no separators) - score 0.3
        ("BAB1234", 1, ((0, 7),), ((0.3, 1.0),)),
        ("MXYZ123", 1, ((0, 7),), ((0.3, 1.0),)),

        # With surrounding text
        ("My license plate is B-AB 1234", 1, ((20, 29),), ((0.5, 1.0),)),
        ("Fahrzeug: M-XY 123", 1, ((10, 18),), ((0.5, 1.0),)),

        # Multiple plates (space format)
        ("Plates: B AB 1234 and M XY 123", 2, ((8, 17), (22, 30)), ((0.3, 1.0), (0.3, 1.0))),

        # Invalid - no numbers
        ("B AB CDEF", 0, (), ()),

        # Invalid - only numbers
        ("1234 5678", 0, (), ()),

        # Invalid - 4-letter district codes don't exist in Germany
        ("ABCD 1234", 0, (), ()),

        # Invalid - double hyphen format is not standard
        ("M-XY-123", 0, (), ()),
        # fmt: on
    ],
)
def test_when_license_plate_in_text_then_all_found(
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
        # Valid format - letters and numbers
        ("BAB1234", None),
        ("M XY 123", None),
        # Invalid - no numbers
        ("B AB CDEF", False),
        # Invalid - only numbers
        ("1234 5678", False),
    ],
)
def test_validate_result(text, expected, recognizer):
    """Test the validate_result method directly."""
    result = recognizer.validate_result(text)
    assert result == expected


def test_recognizer_initialization():
    """Test recognizer initialization with default parameters."""
    recognizer = DeLicensePlateRecognizer()
    assert recognizer.supported_entities == ["DE_LICENSE_PLATE"]
    assert recognizer.supported_language == "de"
    assert len(recognizer.patterns) == 3
    assert len(recognizer.context) > 0
