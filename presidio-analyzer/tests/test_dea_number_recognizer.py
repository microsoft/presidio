import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import DrugEnforcementAgencyNumberRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DrugEnforcementAgencyNumberRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DEA_NUMBER"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # fmt: off
        ("BE1234563", 1, ((0, 9),),),
        ("Gn2494932", 1, ((0, 9),),),
        ("Gz1234563", 1, ((0, 9),),),

        # Invalid DEA Numbers
        ("cA3561105", 0, (),),
        ("Nu2494932", 0, (),),
        # fmt: on
    ],
)
def test_when_all_dea_then_succeed(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (start, end) in zip(results, expected_positions):

        assert_result(res, entities[0], start, end, max_score)
