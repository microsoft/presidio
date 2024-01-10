import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import LtNationalIdNumberRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return LtNationalIdNumberRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["LT_ASMENS_KODAS"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # fmt: off
        # valid identity card scores
        ("33309240064", 1, ((0, 11),),),
        # invalid identity card scores
        ("33309240063", 0, ()),
        ("99999999999", 0, ()),
        # fmt: on
    ],
)
def test_when_all_lt_numbers_then_succeed(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, max_score)
