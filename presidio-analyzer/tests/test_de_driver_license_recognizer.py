import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DeDriverLicenseRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeDriverLicenseRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_DRIVER_LICENSE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid EU format patterns (alphanumeric)
        ("B0721234567", 1, ((0, 11),), ((0.1, 1.0),)),
        ("AB1234567890", 1, ((0, 12),), ((0.1, 1.0),)),
        ("M123456789X", 1, ((0, 11),), ((0.1, 1.0),)),

        # With surrounding text
        ("License: B0721234567 issued", 1, ((9, 20),), ((0.1, 1.0),)),
        ("Fuhrerschein Nr. AB1234567890", 1, ((17, 29),), ((0.1, 1.0),)),

        # Multiple licenses
        ("Licenses B0721234567 and AB1234567890", 2, ((9, 20), (25, 37)), ((0.1, 1.0), (0.1, 1.0))),

        # Invalid - too short
        ("B072123", 0, (), ()),

        # Invalid - only letters
        ("ABCDEFGHIJK", 0, (), ()),

        # Invalid - only digits
        ("12345678901", 0, (), ()),
        # fmt: on
    ],
)
def test_when_driver_license_in_text_then_all_licenses_found(
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
        # Valid - contains both letters and numbers, correct length
        ("B0721234567", None),  # Returns None (no definitive validation)
        ("AB1234567890", None),
        # Invalid - too short
        ("B07212", False),
        # Invalid - only letters
        ("ABCDEFGHIJK", False),
        # Invalid - only digits
        ("12345678901", False),
    ],
)
def test_validate_result(text, expected, recognizer):
    """Test the validate_result method directly."""
    result = recognizer.validate_result(text)
    assert result == expected


def test_recognizer_initialization():
    """Test recognizer initialization with default parameters."""
    recognizer = DeDriverLicenseRecognizer()
    assert recognizer.supported_entities == ["DE_DRIVER_LICENSE"]
    assert recognizer.supported_language == "de"
    assert len(recognizer.patterns) == 2
    assert len(recognizer.context) > 0
