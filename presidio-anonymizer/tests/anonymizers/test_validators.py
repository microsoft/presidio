import pytest

from presidio_anonymizer.anonymizers.validators import validate_parameter
from presidio_anonymizer.anonymizers.validators import validate_type
from presidio_anonymizer.entities import InvalidParamException


def test_when_parameter_is_none_typed_then_ipe_raised():
    with pytest.raises(InvalidParamException, match="Expected parameter name"):
        validate_parameter(
            parameter_value=None, parameter_name="name", parameter_type=int
        )


def test_when_parameter_is_bad_typed_then_ipe_raised():

    with pytest.raises(
        InvalidParamException,
        match="Invalid parameter value for name. Expecting 'number', but got 'string'.",
    ):
        validate_parameter(
            parameter_value="1", parameter_name="name", parameter_type=int
        )


def test_when_actual_parameter_is_non_json_typed_then_ipe_raised_with_general_error():
    with pytest.raises(
            InvalidParamException, match="Invalid parameter value for 'name'."
    ):
        validate_parameter(
            parameter_value="1", parameter_name="name", parameter_type=tuple
        )


def test_given_wrong_type_then_we_fail():
    err_str = "Invalid parameter value for name. Expecting 'string', but got 'number'."
    with pytest.raises(
            InvalidParamException,
            match=err_str
    ):
        validate_type(
            parameter_value=1, parameter_name="name", parameter_type=str
        )


def test_given_right_type_then_we_pass():
    validate_type(
        parameter_value="1", parameter_name="name", parameter_type=str
    )


def test_given_none_type_then_we_pass():
    validate_type(
        parameter_value=None, parameter_name="name", parameter_type=str
    )
