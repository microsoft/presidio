import pytest

from presidio_anonymizer.manipulators import Redact


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
    text = Redact().manipulate("", params)
    assert text == ""


def test_when_validate_anonymizer_then_correct_name():
    assert Redact().manipulator_name() == "redact"
