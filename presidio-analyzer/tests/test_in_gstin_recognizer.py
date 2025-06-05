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
        ("29ABCDE1234F1Z5", 1, (0, 15), 0.5), 
        ("07ABCDE1234G1Z3", 1, (0, 15), 0.5), 
        ("My GST number is 27ABCDE1234H1Z9 and it's active", 1, (17, 32), 0.5), 
        ("This is not a GSTIN: ABCDE1234F1Z5", 0, (), ()), 
        ("GSTIN: 99ABCDE1234L1Z1", 1, (7, 22), 0.5), 
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
