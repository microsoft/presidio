import pytest

from presidio_anonymizer.operators import Custom
from presidio_anonymizer.entities import InvalidParamException


def test_given_value_for_custom_then_we_get_the_value_back():
    text = Custom().operate("", {"new_value": "bla"})
    assert text == "bla"


def test_given_lambda_for_custom_we_get_the_result_back():
    text = Custom().operate("bla", {"new_value" : lambda x: x[::-1]})
    assert text == "alb"


def test_given_non_str_lambda_than_ipe_raised():
    with pytest.raises(
        InvalidParamException,
        match="Invalid method return type. must be a str",
    ):
        Custom().validate({"new_value" : lambda x: len(x)})


def test_when_validate_anonymizer_then_correct_name():
    assert Custom().operator_name() == "custom"
