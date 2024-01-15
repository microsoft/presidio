import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import InAadhaarRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return InAadhaarRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["IN_AADHAAR"]


@pytest.mark.parametrize(
    "text, expected_len, expected_position, expected_score",
    [
        # fmt: off
        ("123456789012", 0, (0,12), 0),
        ("312345678909", 1, (0, 12), 1),
        ("399876543211", 1, (0, 12), 1),
        ("My Aadhaar number is 400123456787 with a lot of text beyond it", 1, (21,33), 1),
        # fmt: on
    ],
)
def test_when_aadhaar_in_text_then_all_aadhaars_found(
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
