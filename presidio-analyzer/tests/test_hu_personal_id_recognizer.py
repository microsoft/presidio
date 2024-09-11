import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import HuPersonalIdentificationRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return HuPersonalIdentificationRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["HU_PERSONAL_IDENTIFICATION_NUMBER"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        ("19410202444", 1, ((0, 11),),((0.0, 1.0),),),

        # Invalid Hu Id Numbers
        ("18709189997", 0, ((0, 11),),((0.0, 0.5),),),
        ("27504310005", 0, ((0, 11),),((0.0, 0.5),),),
        
        # fmt: on
    ],
)
def test_when_all_hu_id_then_succeed(
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
