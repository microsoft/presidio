import pytest

from presidio_anonymizer.operators import Custom
from presidio_anonymizer.entities import InvalidParamError


def test_given_non_callable_for_custom_then_ipe_raised():
    with pytest.raises(
        InvalidParamError,
        match="New value must be a callable function",
    ):
        Custom().validate({"lambda": "bla"})


def test_given_lambda_for_custom_we_get_the_result_back():
    text = Custom().operate("bla", {"lambda": lambda x: x[::-1]})
    assert text == "alb"


def test_given_non_str_lambda_than_ipe_raised():
    with pytest.raises(
        InvalidParamError,
        match="Function return type must be a str",
    ):
        Custom().validate({"lambda": lambda x: len(x)})


def test_when_validate_anonymizer_then_correct_name():
    assert Custom().operator_name() == "custom"
