import pytest

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.operators import OperatorType
from tests.operators.mock_operators_utils import OperatorsFactory, setup_function, teardown_function, resetOperatorsFactory, custom_indirect_operator

def test_given_anonymizers_list_then_all_classes_are_there():
    anonymizers = OperatorsFactory.get_anonymizers()
    assert len(anonymizers) == 9
    for class_name in [
        "hash",
        "mask",
        "redact",
        "replace",
        "encrypt",
        "custom",
        "keep",
        "encrypt2",
        "encrypt3"
    ]:
        assert anonymizers.get(class_name)


def test_given_decryptors_list_then_all_classes_are_there():
    decryptors = OperatorsFactory.get_deanonymizers()
    assert len(decryptors) == 3
    for class_name in ["decrypt", "decrypt2", "decrypt3"]:
        assert decryptors.get(class_name)


def test_given_anonymize_operators_class_then_we_get_the_correct_class():

    for operator_name in ["hash", "mask", "redact", "replace", "encrypt", "custom",
                           "encrypt3", "encrypt2"]:
        resetOperatorsFactory()
        if operator_name == "encrypt3":
            #encrypt3 inherits Operator directly
            from tests.operators.mock_operators  import Encrypt3
        if operator_name == "encrypt2":
            #encrypt3 inherits Operator inderactely
            #first lets unload encrypt3 module
            del Encrypt3
            #now, lets import encrypt2
            from tests.operators.mock_operators import Encrypt2



        operator = OperatorsFactory().create_operator_class(
            operator_name, OperatorType.Anonymize
        )
        assert operator
        assert operator.operator_name() == operator_name
        assert (
            operator.operator_type() == OperatorType.Anonymize
            or operator.operator_type() == OperatorType.All
        )

    resetOperatorsFactory()
    del Encrypt2

def test_given_direct_custom_anonymize_operator_then_we_get_the_correct_class():

    from tests.operators.mock_operators import Encrypt3
    del Encrypt3

def test_given_indirect_custom_anonymize_operator_then_we_get_the_correct_class():

    from tests.operators.mock_operators import Encrypt2
    del Encrypt2

def test_given_direct_custom_deanonymize_operator_then_we_get_the_correct_class():

    from tests.operators.mock_operators import Decrypt3
    del Decrypt3


def test_given_indirect_custom_deanonymize_operator_then_we_get_the_correct_class():

    from tests.operators.mock_operators import Decrypt3
    del Decrypt3


def test_given_decrypt_operator_class_then_we_get_the_correct_class():
    for operator_name in ["decrypt"]:
        operator = OperatorsFactory().create_operator_class(
            operator_name, OperatorType.Deanonymize
        )
        assert operator
        assert operator.operator_name() == operator_name
        assert operator.operator_type() == OperatorType.Deanonymize


def test_given_wrong_name_class_then_we_fail():
    with pytest.raises(
        InvalidParamException, match="Invalid operator class 'encrypt'."
    ):
        OperatorsFactory().create_operator_class("encrypt", OperatorType.Deanonymize)


def test_given_wrong_name_for_anonymizer_class_then_we_fail():
    with pytest.raises(
        InvalidParamException, match="Invalid operator class 'decrypt'."
    ):
        OperatorsFactory().create_operator_class("decrypt", OperatorType.Anonymize)


def test_given_wrong_operator_then_we_fail():
    with pytest.raises(InvalidParamException, match="Invalid operator type '3'."):
        OperatorsFactory().create_operator_class("bla", 3)
