import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers.country_specific.korea.kr_frn_recognizer import KrFrnRecognizer

@pytest.fixture(scope="module")
def recognizer():
    return KrFrnRecognizer()

@pytest.fixture(scope="module")
def entities():
    return ["KR_FRN"]

@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # Valid FRNs, but medium match
        ("911124-5678901", 1, ((0, 14),), ((0.5, 0.5),), ),
        ("9111245678901", 1, ((0, 13),), ((0.5, 0.5),), ),
        ("000505-7637892", 1, ((0, 14),), ((0.5, 0.5),), ),
        ("0005056637892", 1, ((0, 13),), ((0.5, 0.5),), ),
        ("His Korean FRN is 911124-5678901", 1, ((18, 32),), ((0.5, 0.5),), ),

        # Valid FRNs, strong match by validate_result()
        ("911124-5678906", 1, ((0, 14),), ((1.0, 1.0),), ),
        ("9111245678906", 1, ((0, 13),), ((1.0, 1.0),), ),
        ("050912-6000012", 1, ((0, 14),), ((1.0, 1.0),), ),
        ("0509126000012", 1, ((0, 13),), ((1.0, 1.0),), ),
        ("His FRN is 9111245678906", 1, ((11, 24),), ((1.0, 1.0),), ),

        # Invalid FRNs 
        ("001332-1234567", 0, (), (),),
        ("0013321234567", 0, (), (),),
        ("960121+1021413", 0, (), (),),
        ("960111-10214131", 0, (), (),),
        ("960303-0021413", 0, (), (),),
        ("760413-1212134", 0, (), (),),
        ("000402-2214431", 0, (), (),),
        ("051102-9234110", 0, (), (),),
    ],
)
def test_when_all_frns_then_succeed(
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
