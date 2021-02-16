import pytest

from presidio_image_redactor.entities import InvalidParamException
from presidio_image_redactor.entities.api_request_convertor import (
    get_json_data,
    color_fill_string_to_value,
)


def test_given_no_data_then_we_get_default_dict():
    assert get_json_data("") == {}


@pytest.mark.parametrize(
    # fmt: off
    "str_json",
    [
        '{\'color_fill\': \'0, 0, 1\'}',
        "{'color_fill': '0, 0, 1'}",
        "{\"color_fill\": \"0, 0, 1\"}",
    ],
    # fmt: on
)
def test_given_json_string_then_we_get_json_back(str_json):
    assert get_json_data(str_json) == {"color_fill": "0, 0, 1"}


def test_given_invalid_json_string_then_we_get_an_invalid_param_exception():
    with pytest.raises(InvalidParamException, match="Invalid json format 'not_json'"):
        get_json_data("not_json")


def test_given_empty_json_params_then_we_send_default_color_fill():
    assert color_fill_string_to_value({}) == (0, 0, 0)


@pytest.mark.parametrize(
    # fmt: off
    "json_params,expected_result",
    [
        ({"color_fill": "1"}, 1),
        ({"color_fill": "1, 0, 1"}, (1, 0, 1))
    ],
    # fmt: on
)
def test_given_json_params_then_we_extract_properly_color_fill(
    json_params, expected_result
):
    assert color_fill_string_to_value(json_params) == expected_result


@pytest.mark.parametrize(
    # fmt: off
    "json_params,data",
    [
        ({"color_fill": "1, 0, 1, 0"}, "1, 0, 1, 0"),
        ({"color_fill": "1, 0"}, "1, 0")
    ],
    # fmt: on
)
def test_given_json_params_then_we_fail_to_extract_properly_color_fill(
    json_params, data
):
    with pytest.raises(InvalidParamException, match=f"Invalid color fill '{data}'"):
        color_fill_string_to_value(json_params)


def test_given_invalid_color_fill_then_get_an_invalid_param_exception():
    with pytest.raises(InvalidParamException, match="Invalid color fill 'bla'"):
        color_fill_string_to_value({"color_fill": "bla"})
