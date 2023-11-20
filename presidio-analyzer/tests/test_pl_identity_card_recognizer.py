import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import PlIdentityCardRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return PlIdentityCardRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["PL_IDENTITY_CARD"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # fmt: off
        # valid identity card scores
        # example from: https://www.gov.pl/web/gov/dowod-osobisty-informacje
        ("ZZC108201", 1, ((0, 9),),),
        # invalid identity card scores
        ("123123456", 0, ()),
        ("ABCD12345", 0, ()),
        ("ABC-123456", 0, ()),
        ("zzc108201", 0, ()),
        # fmt: on
    ],
)
def test_when_all_pl_identity_card_then_succeed(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, max_score)
