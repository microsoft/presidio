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
    with pytest.raises(InvalidParamException, match='Invalid json format \'not_json\''):
        Server()._get_json_data("not_json")
