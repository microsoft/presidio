import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import SgFinRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return SgFinRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["SG_NRIC_FIN"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_scores",
    [
        ("G1122144L", 2, ((0, 9), (0, 9),), (0.3, 0.5),),  # should this be only 1?
        ("PA12348L", 0, (), (),),
    ],
)
def test_all_sg_fins(
    text, expected_len, expected_positions, expected_scores, recognizer, entities,
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, score, (st_pos, fn_pos) in zip(
        results, expected_scores, expected_positions
    ):
        assert_result(res, entities[0], st_pos, fn_pos, score)
