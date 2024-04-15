import pytest           
from presidio_analyzer.predefined_recognizers import InPassportRecognizer
# from tests import assert_result
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
        ("A3456781", 1, (0,8), 0.7),
        ("B3097651", 1, (0,8), 0.7),
        ("C3590543", 1, (0,8), 0.7),
        ("my passport number is T3569075", 1, (22,30), 0.7),
        ("passport number: J6932157", 1, (17,25), 0.7),

        #Invalid Passport Numbers
        ("A3456781", 0, (0,8), 0),
        ("b0097650", 0, (), 0),
        ("my passport number is t3569075", 0, (), 0),
        # fmt: on
    ],
)
def test_when_all_passport_numers_then_succeed(
        text,
        expected_len,
        expected_position,
        expected_score,
        recognizer,
        entities,
):
    results = recognizer.analyze(text, entities)
    if results:
        assert_result(
            results[0],
            entities[0],
            expected_position[0],
            expected_position[1],
            expected_score,
        )
