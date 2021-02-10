import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import AbaRoutingRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return AbaRoutingRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["ABA_ROUTING_NUMBER"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score",
    [
        # fmt: off
        # Bank of America
        ("121000358", 1, ((0, 9),), 1.0),
        # Chase
        ("3222-7162-7", 1, ((0, 11),), 1.0),
        # Wells Fargo
        ("121042882", 1, ((0, 9),), 1.0),
        ("0711-0130-7", 1, ((0, 11),), 1.0),
        # invalid ABA numbers
        ("421042111", 0, (), -1.0),
        ("1234-0000-0", 0, (), -1.0),
        # fmt: on
    ],
)
def test_when_aba_routing_numbers_then_succeed(
    text, expected_len, expected_positions, expected_score, recognizer, entities
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, expected_score)
