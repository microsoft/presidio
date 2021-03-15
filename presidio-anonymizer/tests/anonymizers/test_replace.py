import pytest

from presidio_anonymizer.manipulators import Replace


def test_given_value_for_replace_then_we_get_the_value_back():
    text = Replace().manipulate("", {"new_value": "bla"})
    assert text == "bla"


@pytest.mark.parametrize(
    # fmt: off
    "params, result",
    [
        ({"entity_type": ""}, "<>"),
        ({"new_value": "", "entity_type": ""}, "<>"),
        ({"entity_type": "PHONE_NUMBER"}, "<PHONE_NUMBER>"),
        ({"new_value": "", "entity_type": "PHONE_NUMBER"}, "<PHONE_NUMBER>"),
    ],
    # fmt: on
)
def test_given_no_value_for_replace_then_we_return_default_value_from_entity_type(
    params, result
):
    text = Replace().manipulate("", params)
    assert text == result


def test_when_validate_anonymizer_then_correct_name():
    assert Replace().manipulator_name() == "replace"
