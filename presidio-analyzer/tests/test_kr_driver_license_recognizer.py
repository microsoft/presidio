import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import KrDriverLicenseRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return KrDriverLicenseRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["KR_DRIVER_LICENSE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid license numbers with correct regional codes (e.g., 11 for Seoul)
        ("11-22-123456-12", 1, ((0, 15),), ((1.0, 1.0),), ),
        ("112212345612", 1, ((0, 12),), ((1.0, 1.0),), ),
        ("My license is 13-22-123456-12", 1, ((14, 29),), ((1.0, 1.0),), ),

        # Valid regional code (e.g., 28) with space delimiters
        ("28 22 123456 12", 1, ((0, 15),), ((1.0, 1.0),), ),

        # Invalid regional code: 99 is not a registered area code in Korea
        # Should be filtered out by validate_result()
        ("99-22-123456-12", 0, (), (),), 

        # Invalid format: Incorrect number of digits in the serial or check part
        ("11-22-12345-12", 0, (), (),),  # 5 digits instead of 6
        ("11-22-123456-1", 0, (), (),),   # 1 digit instead of 2

        # Invalid characters: Contains non-digit characters
        ("11-22-123A56-12", 0, (), (),),

        # Boundary test: Ensure lookaround prevents matching part of a longer digit string
        ("111-22-123456-12", 0, (), (),),
        ("11-22-123456-123", 0, (), (),),
        # fmt: on
    ],
)
def test_when_all_driver_licenses_then_succeed(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
):
    """
    Test the recognition of Korean Driver's License numbers.
    The score is expected to be 1.0 for valid patterns and regional codes,
    as the checksum logic is not publicly available for full validation.
    """
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )
