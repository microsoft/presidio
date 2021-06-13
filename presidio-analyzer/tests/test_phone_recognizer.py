import pytest

from presidio_analyzer.predefined_recognizers.phone_recognizer import PhoneRecognizer
from tests import assert_result


@pytest.fixture(scope="module")
def recognizer():
    return PhoneRecognizer()


@pytest.mark.parametrize(
    "text, expected_len, entities, expected_positions, max_score",
    [
        # fmt: off
        ("My US number is (415) 555-0132, and my international one is +1 415 555 0132",
         2, ["INTERNATIONAL_PHONE_NUMBER", "US_PHONE_NUMBER"],
         ((60, 75), (16, 30),), 0.6),
        ("My Israeli number is 09-7625400", 0,
         ["INTERNATIONAL_PHONE_NUMBER", "US_PHONE_NUMBER"], ((60, 75), (16, 30),), 0.6),
        ("My Israeli number is 09-7625400", 1, ["IL_PHONE_NUMBER"], ((21, 31), ), 0.6),
        ("My Israeli number is 09-7625400", 2,
         PhoneRecognizer().get_supported_entities(), (2 * ()), 0.6),
        # fmt: on
    ],
)
def test_when_all_cryptos_then_succeed(
    text,
    expected_len,
    entities,
    expected_positions,
    max_score,
    recognizer,
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for i, (res, (st_pos, fn_pos)) in enumerate(zip(results, expected_positions)):
        assert_result(res, entities[i], st_pos, fn_pos, max_score)
