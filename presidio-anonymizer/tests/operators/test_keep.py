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
def test_given_value_for_redact_then_we_return_empty_value(params):
    text = Keep().operate("bla", params)
    assert text == "bla"


def test_when_validate_anonymizer_then_correct_name():
    assert Keep().operator_name() == "keep"
