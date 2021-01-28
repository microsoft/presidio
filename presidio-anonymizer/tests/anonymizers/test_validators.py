import pytest

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.anonymizers.validators import validate_parameter


def test_validate_parameter_when_parameter_is_none_typed_ipe_raised():

    with pytest.raises(InvalidParamException, match="Expected parameter name"):
        validate_parameter(
            parameter_value=None, parameter_name="name", parameter_type=int
        )


def test_validate_parameter_when_parameter_is_bad_typed_ipe_raised():

    with pytest.raises(
        InvalidParamException, match="Invalid parameter value for 'name'"
    ):
        validate_parameter(
            parameter_value="1", parameter_name="name", parameter_type=int
        )
