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
    "text, expected_len, expected_position, expected_score",
    [
        # fmt: off
        ("G1122144L", 1, (0, 9), 0.5), ("PA12348L", 0, (), (),)
        # fmt: on
    ],
)
def test_when_sgfins_in_text_then_all_sg_fins_found(
    text,
    expected_len,
    expected_position,
    expected_score,
    recognizer,
    entities,
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    if results:
        assert_result(
            results[0],
            entities[0],
            expected_position[0],
            expected_position[1],
            expected_score,
        )
