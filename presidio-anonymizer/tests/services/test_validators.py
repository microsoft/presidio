import pytest

from presidio_anonymizer.entities import InvalidParamError
from presidio_anonymizer.services.validators import (
    validate_parameter,
    validate_parameter_exists,
    validate_parameter_in_range,
    validate_parameter_not_empty,
    validate_type,
)


def test_given_parameter_is_0_then_no_exception_raised():
    validate_parameter_exists(0, "entity", "name")


def test_given_empty_string_then_no_exception_raised():
    validate_parameter_exists("", "entity", "name")


def test_given_no_existing_parameter_then_exception_raised():
    with pytest.raises(
        InvalidParamError,
        match="Invalid input, entity must contain name",
    ):
        validate_parameter_exists(None, "entity", "name")


def test_given_existing_parameter_then_no_exception_raised():
    validate_parameter_not_empty("1234", "entity", "name")


def test_given_empty_parameter_then_exception_raised():
    with pytest.raises(
        InvalidParamError,
        match="Invalid input, entity must contain name",
    ):
        validate_parameter_not_empty("", "entity", "name")


def test_given_parameter_does_not_exist_then_exception_raised():
    with pytest.raises(
        InvalidParamError,
        match="Invalid input, entity must contain name",
    ):
        validate_parameter_not_empty(None, "entity", "name")


def test_given_parameter_is_0_then_exception_raised():
    with pytest.raises(
        InvalidParamError,
        match="Invalid input, entity must contain name",
    ):
        validate_parameter_not_empty(0, "entity", "name")


def test_given_parameter_not_in_range_then_ipe_raised():
    with pytest.raises(
        InvalidParamError,
        match="Parameter name value 1 is not in range of values \\['0', '2'\\]",
    ):
        validate_parameter_in_range(
            values_range=["0", "2"],
            parameter_value="1",
            parameter_name="name",
            parameter_type=str,
        )


def test_given_parameter_in_range_then_we_pass():
    validate_parameter_in_range(
        values_range=["1", "2"],
        parameter_value="1",
        parameter_name="name",
        parameter_type=str,
    )


def test_given_parameter_is_none_typed_then_ipe_raised():
    with pytest.raises(InvalidParamError, match="Expected parameter name"):
        validate_parameter(
            parameter_value=None, parameter_name="name", parameter_type=int
        )


def test_given_parameter_is_bad_typed_then_ipe_raised():
    err = "Invalid parameter value for name. Expecting 'number', but got 'string'."
    with pytest.raises(
        InvalidParamError,
        match=err,
    ):
        validate_parameter(
            parameter_value="1", parameter_name="name", parameter_type=int
        )


def test_given_actual_parameter_is_non_json_typed_then_ipe_raised_with_general_error():
    with pytest.raises(
        InvalidParamError, match="Invalid parameter value for 'name'."
    ):
        validate_parameter(
            parameter_value="1", parameter_name="name", parameter_type=tuple
        )


def test_given_wrong_type_then_we_fail():
    err_str = "Invalid parameter value for name. Expecting 'string', but got 'number'."
    with pytest.raises(InvalidParamError, match=err_str):
        validate_type(parameter_value=1, parameter_name="name", parameter_type=str)


def test_given_right_type_then_we_pass():
    validate_type(parameter_value="1", parameter_name="name", parameter_type=str)


def test_given_none_type_then_we_pass():
    validate_type(parameter_value=None, parameter_name="name", parameter_type=str)
