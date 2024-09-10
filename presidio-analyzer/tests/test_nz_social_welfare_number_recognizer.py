import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import NZSocialWelfareNumberRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return NZSocialWelfareNumberRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["NZ_SWN"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        ("799-011-542", 1, ((0, 10),), ((0.0, 0.4),),),
        ("110653022", 1, ((0, 9),), ((0.0, 0.4),),),
        # fmt: on
    ],
)
def test_when_all_nz_swn_found_then_succeed(
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
