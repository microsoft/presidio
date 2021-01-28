"""Anomnymizers validations utility methods."""
from presidio_anonymizer.entities import InvalidParamException


def validate_parameter(
    parameter_value, parameter_name: str, parameter_type: type
) -> None:
    """Validate an anonymizer parameter.

    Both validate the existence of an anonymizer parameter and that it is an
    instance of the parameter_type. Otherwise, raise the appropriate
    InvalidParamException with the parameter_name as content.
    """
    if parameter_value is None:
        raise InvalidParamException(f"Expected parameter {parameter_name}")
    if not isinstance(parameter_value, parameter_type):
        message = _get_bad_typed_parameter_error_message(
            parameter_name,
            expected_type=parameter_type,
            actual_type=type(parameter_value),
        )
        raise InvalidParamException(message)


def _get_bad_typed_parameter_error_message(parameter_name, expected_type, actual_type):
    type_to_json_type = {
        str: "string",
        bool: "boolean",
        int: "number",
        list: "array",
        object: "object",
    }
    expected_type_display_name = type_to_json_type.get(expected_type)
    actual_type_display_name = type_to_json_type.get(actual_type)
    if expected_type_display_name and actual_type_display_name:
        return (
            f"Invalid parameter value for {parameter_name}. "
            f"Expecting '{expected_type_display_name}', "
            f"but got '{actual_type_display_name}'."
        )
    else:
        return f"Invalid parameter value for '{parameter_name}'."
