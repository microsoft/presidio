import pytest           
from presidio_analyzer.predefined_recognizers import InPassportRecognizer
from tests.assertions import assert_result

@pytest.fixture(scope="module")
def recognizer():
    return InPassportRecognizer()

@pytest.fixture(scope="module")
def entities():
    return ["IN_PASSPORT"]

@pytest.mark.parametrize(
    "text, expected_len, expected_position, expected_score",
    [
        # fmt: off
        #Valid Passport Numbers
        ("A3456781", 1, (0,8), 0.1),
        ("B3097651", 1, (0,8), 0.1),
        ("C3590543", 1, (0,8), 0.1),
        ("my passport number is T3569075", 1, (22,30), 0.1),
        ("passport number: J6932157", 1, (17,25), 0.1),

        #Invalid Passport Numbers
        ("b0097650", 0, (), 0),
        ("my passport number is T356907", 0, (), 0),
        # fmt: on
    ],
)
def test_when_all_passport_numbers_then_succeed(
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
