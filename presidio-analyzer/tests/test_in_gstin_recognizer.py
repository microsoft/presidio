import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import InGstinRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return InGstinRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["IN_GSTIN"]


@pytest.mark.parametrize(
    "text, expected_len, expected_position, expected_score",
    [
        # fmt: off
        ("09ACQPI2284L1Z0", 1, (0, 15), 1),
        ("99ABCPG1111T1NX", 0, (0, 15), 1),
        ("03AAGFL0883Q2ZW", 1, (0, 15), 1),
        ("9917USA00015OS3", 1, (0, 15), 0.6),
        ("My GSTIN is 29AAHCR6226R1ZJ with a lot of text beyond it", 1, (12, 27), 1),
        # fmt: on
    ],
)
def test_when_gstin_in_text_then_all_gstins_found(
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
