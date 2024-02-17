import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import SgFinRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return SgFinRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["SG_NRIC_FIN"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        ## Medium match
        # Test with valid NRIC/FIN starting with S
        ("S2740116C", 1, [(0, 9)], [(0.5, 0.8)]),
        # Test with valid NRIC/FIN starting with T
        ("T1234567Z", 1, [(0, 9)], [(0.5, 0.8)]),
        # Test with valid NRIC/FIN starting with F
        ("F2346401L", 1, [(0, 9)], [(0.5, 0.8)]),
        # Test with valid NRIC/FIN starting with G
        ("G1122144L", 1, [(0, 9)], [(0.5, 0.8)]),
        # Test with valid NRIC/FIN starting with M
        ("M4332674T", 1, [(0, 9)], [(0.5, 0.8)]),
        # Test with multiple valid NRIC/FINs
        ("S9108268C T7572225C", 2, [(0, 9), (10, 19)], [(0.5, 0.8)] * 2),
        # Test with valid NRIC/FIN in a sentence
        ("NRIC S2740116C was processed", 1, [(5, 14)], [(0.5, 0.8)]),

        # ## Weak match
        # Test with invalid NRIC/FIN starting with A
        ("A1234567Z", 1, [(0, 9)], [(0, 0.3)]),
        # # Test with invalid NRIC/FIN starting with B
        ("B1234567Z", 1, [(0, 9)], [(0, 0.3)]),
        
        ## No match
        # Test with invalid length
        ("PA12348L", 0, [], []),
        # Test with empty string
        ("", 0, [], []),
        # fmt: on
    ],
)
def test_when_sgfins_in_text_then_all_sg_fins_found(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
    max_score,
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len

    for result, (start_pos, end_pos), (start_score, end_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        import logging
        logging.info(f"result: {result}")
        # Adjust end_score if it's marked with a placeholder value that indicates it should be considered as max_score
        if end_score == "max":
            end_score = max_score

        # Assuming assert_result_within_score_range checks the position and verifies the score is within the specified range
        assert_result_within_score_range(
            result, entities[0], start_pos, end_pos, start_score, end_score
        )