import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DePostalCodeRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DePostalCodeRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_POSTAL_CODE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid postal codes - 5 digits
        ("10115", 1, ((0, 5),), ((0.3, 1.0),)),
        ("80331", 1, ((0, 5),), ((0.3, 1.0),)),
        ("50667", 1, ((0, 5),), ((0.3, 1.0),)),

        # With surrounding text
        ("My postal code is 10115 Berlin", 1, ((18, 23),), ((0.3, 1.0),)),
        ("PLZ: 80331 Munich", 1, ((5, 10),), ((0.3, 1.0),)),

        # Multiple postal codes
        ("10115 and 80331", 2, ((0, 5), (10, 15)), ((0.3, 1.0), (0.3, 1.0))),

        # Invalid - too short
        ("1011", 0, (), ()),

        # Invalid - too long
        ("101150", 0, (), ()),

        # Postal codes starting with 0 ARE valid in Germany (eastern regions)
        ("01234", 1, ((0, 5),), ((0.3, 1.0),)),

        # Invalid - contains letters
        ("1011A", 0, (), ()),
        # fmt: on
    ],
)
def test_when_postal_code_in_text_then_all_found(
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
        # Valid postal codes
        ("10115", None),  # Berlin
        ("80331", None),  # Munich
        # Invalid - too short
        ("1011", False),
        # Invalid - too long
        ("101150", False),
        # Invalid - contains letters
        ("1011A", False),
    ],
)
def test_validate_result(text, expected, recognizer):
    """Test the validate_result method directly."""
    result = recognizer.validate_result(text)
    assert result == expected


def test_recognizer_initialization():
    """Test recognizer initialization with default parameters."""
    recognizer = DePostalCodeRecognizer()
    assert recognizer.supported_entities == ["DE_POSTAL_CODE"]
    assert recognizer.supported_language == "de"
    assert len(recognizer.patterns) == 1
    assert len(recognizer.context) > 0
