import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import KrRrnRecognizer

@pytest.fixture(scope="module")
def recognizer():
    return KrRrnRecognizer()

@pytest.fixture(scope="module")
def entities():
    return ["KR_RRN"]

@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # Valid RRNs, but medium match
        ("960121-1234567", 1, ((0, 14),), ((0.5, 0.5),), ),
        ("9601211234567", 1, ((0, 13),), ((0.5, 0.5),), ),
        ("000505-7637892", 1, ((0, 14),), ((0.5, 0.5),), ),
        ("0005057637892", 1, ((0, 13),), ((0.5, 0.5),), ),
        ("His Korean RRN is 960121-1234567", 1, ((18, 32),), ((0.5, 0.5),), ),
        
        # Valid RRNs, strong match by validate_result()
        ("960121-1021413", 1, ((0, 14),), ((1.0, 1.0),), ),
        ("9601211021413", 1, ((0, 13),), ((1.0, 1.0),), ),
        ("050912-0000008", 1, ((0, 14),), ((1.0, 1.0),), ),
        ("0509120000008", 1, ((0, 13),), ((1.0, 1.0),), ),
        ("His RRN is 9601211021413", 1, ((11, 24),), ((1.0, 1.0),), ),
        
        # Invalid RRNs 
        ("001332-1234567", 0, (), (),),
        ("0013321234567", 0, (), (),),
        ("960121+1021413", 0, (), (),),
        ("960121-10214131", 0, (), (),),
    ],
)
def test_when_all_rrns_then_succeed(
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
    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        if fn_score == "max":
            fn_score = max_score
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )