import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DeLanrRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeLanrRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_LANR"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid LANR formats with valid checksums
        # Format: 6 digits + check digit + 2 specialty digits
        ("123456601", 1, ((0, 9),), ((0.1, 1.0),)),
        ("987654499", 1, ((0, 9),), ((0.1, 1.0),)),
        ("555555542", 1, ((0, 9),), ((0.1, 1.0),)),

        # With context (higher score)
        ("LANR: 123456601", 1, ((6, 15),), ((0.5, 1.0),)),
        ("Arztnummer 123456601", 1, ((11, 20),), ((0.5, 1.0),)),

        # Invalid - too short
        ("12345678", 0, (), ()),

        # Invalid - too long
        ("1234567890", 0, (), ()),

        # Invalid - contains letters
        ("12345678A", 0, (), ()),

        # Invalid - all zeros
        ("000000000", 0, (), ()),
        # fmt: on
    ],
)
def test_when_lanr_in_text_then_all_found(
    text, expected_len, expected_positions, expected_score_ranges, recognizer, entities
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
        # Valid LANR with valid checksum
        ("123456601", True),
        ("987654499", True),
        # Invalid checksum
        ("123456789", False),
        # Invalid - all zeros
        ("000000000", False),
        # Invalid - wrong length
        ("12345678", False),
    ],
)
def test_validate_result(text, expected, recognizer):
    """Test the validate_result method directly."""
    result = recognizer.validate_result(text)
    assert result == expected


def test_recognizer_initialization():
    recognizer = DeLanrRecognizer()
    assert recognizer.supported_entities == ["DE_LANR"]
    assert recognizer.supported_language == "de"
    assert len(recognizer.patterns) == 2
    assert len(recognizer.context) > 0
