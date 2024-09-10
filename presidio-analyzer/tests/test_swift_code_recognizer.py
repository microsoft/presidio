import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import SWIFTCodeRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return SWIFTCodeRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["SWIFT_CODE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        ("MLCDRUO0", 1, ((0, 8),), ((0.0, 0.3),),),
        ("XHEBSOXIYB9", 1, ((0, 11),), ((0.0, 0.3),),),
        ("CSGXGS4I", 1, ((0, 8),), ((0.0, 0.3),),),
        ("JFNBVHDNFSD", 1, ((0, 11),), ((0.0, 0.3),),),
        # fmt: on
    ],
)
def test_when_all_swift_code_found_then_succeed(
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
