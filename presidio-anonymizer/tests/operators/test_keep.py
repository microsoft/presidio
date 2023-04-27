import pytest

from presidio_anonymizer.operators import Keep


@pytest.mark.parametrize(
    # fmt: off
    "params",
    [
        {"new_value": ""},
        {},
    ],
    # fmt: on
)
def when_given_valid_value_then_same_string_returned(params):
    text = Keep().operate("bla", params)
    assert text == "bla"


def test_when_validate_anonymizer_then_correct_name():
    assert Keep().operator_name() == "keep"
