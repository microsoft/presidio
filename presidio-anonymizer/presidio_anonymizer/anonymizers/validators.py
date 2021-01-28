from presidio_anonymizer.entities import InvalidParamException


def validate_parameter(
    parameter_value, parameter_name: str, parameter_type: type
) -> None:
    """Validate an anonymizer parameter.

    Both validate a parameter exists and that it is an instance of the
    parameter_type. Otherwise, raise the appropriate InvalidParamException
    with the parameter_name as content.
    """
    if not parameter_value:
        raise InvalidParamException(f"Expected parameter {parameter_name}")
    if not isinstance(parameter_value, parameter_type):
        raise InvalidParamException(f"Invalid parameter {parameter_name}")
