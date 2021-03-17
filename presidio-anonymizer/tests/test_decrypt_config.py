import pytest

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.engine import DecryptConfig
from presidio_anonymizer.operators import OperatorType


def test_given_valid_params_then_get_decrypt_config():
    anonymize_config = DecryptConfig("1234")
    assert anonymize_config.operator_type == OperatorType.Decrypt
    assert anonymize_config.operator_name == "decrypt"
    assert anonymize_config.params == {"key": "1234"}


def test_given_no_key_then_we_fail_to_get_decrypt_config():
    expected_error = "Invalid input, config must contain key"
    with pytest.raises(InvalidParamException, match=expected_error):
        DecryptConfig("")
