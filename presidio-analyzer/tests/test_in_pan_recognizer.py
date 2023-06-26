import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import InPanRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return InPanRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["IN_PAN"]


@pytest.mark.parametrize(
    "text, expected_len, expected_position, expected_score",
    [
        # fmt: off
        ("ABCPD1234Z", 1, (0, 9), 0.8), ("AAAA1111R", 0, (), (),)
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
