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
        ("AAASA1111R", 1, (0,10), 0.6) ,
        ("ABCPD1234Z", 1, (0, 10), 0.85),
        ("ABCND1234Z", 1, (0, 10), 0.6),
        ("A1111DFSFS", 1, (0,10),0.05),
        ("ABCD1234",0,(),(),),
        ("My PAN number is ABBPM4567S with a lot of text beyond it", 1, (17,27),.85),
        # fmt: on
    ],
)
def test_when_pan_in_text_then_all_pans_found(
    text,
    expected_len,
    expected_position,
    expected_score,
    recognizer,
    entities,
):
    results = recognizer.analyze(text, entities)
    print(results)

    assert len(results) == expected_len
    if results:
        assert_result(
            results[0],
            entities[0],
            expected_position[0],
            expected_position[1],
            expected_score,
        )
