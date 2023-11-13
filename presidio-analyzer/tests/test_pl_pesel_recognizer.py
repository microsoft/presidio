import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import PlPeselRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return PlPeselRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["PL_PESEL"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # fmt: off
        # valid PESEL scores
        ("11111111114", 1, ((0, 11),),),
        ("My pesel is 11111111114.", 1, ((12, 23), )),
        # invalid PESEL scores
        ("1111321111", 0, ()),
        ("11110021111", 0, ()),
        ("11-11-11-11114", 0, ()),
        # fmt: on
    ],
)
def test_when_all_pl_pesels_then_succeed(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, max_score)
