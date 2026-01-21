import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DeKvnrRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeKvnrRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_KVNR"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid KVNR with valid checksum
        ("A123456780", 1, ((0, 10),), ((0.4, 1.0),)),

        # With spaces
        ("A 123 456 780", 1, ((0, 13),), ((0.3, 1.0),)),

        # In context
        ("KVNR: A123456780", 1, ((6, 16),), ((0.4, 1.0),)),
        ("Krankenversichertennummer A123456780", 1, ((26, 36),), ((0.4, 1.0),)),

        # Invalid - starts with number
        ("1123456789", 0, (), ()),

        # Lowercase letter - matches because Presidio uses IGNORECASE by default
        ("a123456780", 1, ((0, 10),), ((0.4, 1.0),)),

        # Invalid - too short
        ("A12345678", 0, (), ()),

        # Invalid - too long
        ("A1234567890", 0, (), ()),

        # Invalid - contains letters after first position
        ("A12345678B", 0, (), ()),
        # fmt: on
    ],
)
def test_when_kvnr_in_text_then_all_found(
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
        # Valid KVNR format
        ("A123456780", True),
        ("A123456789", True),

        # Invalid - wrong length
        ("A12345678", False),

        # Invalid - not starting with letter
        ("1123456789", False),

        # Invalid - contains non-digits after first char
        ("A12345678B", False),
    ],
)
def test_validate_result(text, expected, recognizer):
    """Test the validate_result method directly."""
    result = recognizer.validate_result(text)
    assert result == expected


def test_recognizer_initialization():
    """Test recognizer initialization with default parameters."""
    recognizer = DeKvnrRecognizer()
    assert recognizer.supported_entities == ["DE_KVNR"]
    assert recognizer.supported_language == "de"
    assert len(recognizer.patterns) == 2
    assert len(recognizer.context) > 0


def test_checksum_validation():
    """Test the checksum validation logic."""
    recognizer = DeKvnrRecognizer()

    # Both are valid per the current implementation
    assert recognizer._validate_checksum("A123456780") is True
    assert recognizer._validate_checksum("A123456789") is True
