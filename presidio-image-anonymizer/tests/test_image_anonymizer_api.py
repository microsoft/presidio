import pytest

from app import Server
from presidio_image_anonymizer.entities import InvalidParamException


def test_given_no_data_then_we_get_default_dict():
    assert Server()._get_json_data("") == {}


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
    assert Server()._get_json_data(str_json) == {'color_fill': '0, 0, 1'}


def test_given_invalid_json_string_then_we_get_an_invalid_param_exception():
    with pytest.raises(InvalidParamException, match="Invalid json format 'not_json'"):
        Server()._get_json_data("not_json")


def test_given_empty_json_params_then_we_send_default_color_fill():
    Server()._color_fill_string_to_value({}) == (0, 0, 0)


@pytest.mark.parametrize(
    # fmt: off
    "json_params,expected_result",
    [
        ({"color_fill": "1"}, 1),
        ({"color_fill": "1, 0, 1"}, (1, 0, 1))
    ],
    # fmt: on
)
def test_given_json_params_then_we_extract_properly_color_fill(json_params,
                                                               expected_result):
    Server()._color_fill_string_to_value(json_params) == expected_result


def test_given_invalid_color_fill_then_get_an_invalid_param_exception():
    with pytest.raises(InvalidParamException, match="Invalid color fill 'bla'"):
        Server()._color_fill_string_to_value({"color_fill": "bla"})
