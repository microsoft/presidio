import pytest
from presidio_analyzer.predefined_recognizers.country_specific.philippines import (
    PhTinRecognizer,
)

from tests import assert_result_within_score_range


@pytest.fixture(scope="module")
def recognizer():
    """Return an instance of the PhTinRecognizer."""
    return PhTinRecognizer()


@pytest.fixture(scope="module")
def entities():
    """Return the entities supported by this recognizer."""
    return ["PH_TIN"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # Valid TINs (using weighted modulo 11: 000-123-456-000 -> rem 6)
        ("My TIN is 000-123-456-000", 1, [(10, 25)], [(0.1, 1.0)]),
        ("BIR TIN: 000123456", 1, [(9, 18)], [(0.1, 1.0)]),
        ("Tax ID: 000-123-456-001", 1, [(8, 23)], [(0.1, 1.0)]),
        # Valid 9-digit with hyphens
        ("TIN 000-123-456", 1, [(4, 15)], [(0.1, 1.0)]),
        # Invalid TINs (wrong checksum)
        ("Invalid TIN 000-123-457-000", 0, [], []),
        ("Not a TIN 123456789", 0, [], []),
        # Context tests
        ("TIN: 000-123-456-000", 1, [(5, 20)], [(0.1, 1.0)]),
        ("Please use 000-123-456-000 as your ID", 1, [(11, 26)], [(0.1, 1.0)]),
    ],
)
def test_ph_tin_recognizer(
    text, expected_len, expected_positions, expected_score_ranges, recognizer, entities
):
    """Test the PhTinRecognizer."""
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    zip_res = zip(results, expected_positions, expected_score_ranges)
    for res, pos, score_range in zip_res:
        assert_result_within_score_range(
            res, entities[0], pos[0], pos[1], score_range[0], score_range[1]
        )
