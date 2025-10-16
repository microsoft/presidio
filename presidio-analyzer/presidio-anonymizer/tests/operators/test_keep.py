import pytest

from presidio_anonymizer.operators import DeanonymizeKeep, Keep


@pytest.mark.parametrize("operator", [Keep, DeanonymizeKeep])
@pytest.mark.parametrize(
    # fmt: off
    ["params"],
    [
        {"new_value": ""},
        {},
    ],
    # fmt: on
)
def when_given_valid_value_then_same_string_returned(params, operator):
    text = operator().operate("bla", params)
    assert text == "bla"


@pytest.mark.parametrize(
    ["operator", "expected_op_name"],
    [(Keep, "keep"), (DeanonymizeKeep, "deanonymize_keep")],
)
def test_when_validate_anonymizer_then_correct_name(operator, expected_op_name):
    assert operator().operator_name() == expected_op_name
