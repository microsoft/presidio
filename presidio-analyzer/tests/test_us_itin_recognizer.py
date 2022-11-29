import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import UsItinRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return UsItinRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["US_ITIN"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        ("911-701234 91170-1234", 2, ((0, 10), (11, 21),), ((0.0, 0.3), (0.0, 0.3),),),
        ("911701234", 1, ((0, 9),), ((0.3, 0.4),),),
        ("911-70-1234", 1, ((0, 11),), ((0.5, 0.6),),),
        ("911-53-1234", 1, ((0, 11),), ((0.5, 0.6),),),
        ("911-64-1234", 1, ((0, 11),), ((0.5, 0.6),),),
        ("911-89-1234", 0, (), (),),
        ("my tax id 911-89-1234", 0, (), (),),
        # fmt: on
    ],
)
def test_when_itin_in_text_then_all_us_itins_found(
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
