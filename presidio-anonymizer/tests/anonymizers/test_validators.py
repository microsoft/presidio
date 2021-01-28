import pytest

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.anonymizers.validators import validate_parameter


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
