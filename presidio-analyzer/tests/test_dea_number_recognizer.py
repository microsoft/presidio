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
        ("MK1466104", 1, ((0, 10),),),
        ("fA0001105", 1, ((0, 10),),),
        ("Gz2355460", 1, ((0, 11),),),
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
