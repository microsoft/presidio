import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import HkIdentityCardRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return HkIdentityCardRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["HK_IDENTITY_NUMBER"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        ("A3056063", 1, ((0, 8),),((0.0, 0.4),),),
        ("AA5437005", 1, ((0, 9),),((0.0, 0.4),),),
        ("A006700(0)", 1, ((0, 10),),((0.0, 0.4),),),
        ("FG006700(9)", 1, ((0, 11),),((0.0, 0.4),),),

        # Invalid HK Id
        ("A006700(P)", 0, (), (),),
        ("FG006700(R)", 0, (), (),),
        # fmt: on
    ],
)
def test_when_all_hk_id_then_succeed(
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
