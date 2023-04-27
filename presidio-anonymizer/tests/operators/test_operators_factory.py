import pytest

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.operators import OperatorsFactory, OperatorType


def test_given_anonymizers_list_then_all_classes_are_there():
    anonymizers = OperatorsFactory.get_anonymizers()
    assert len(anonymizers) == 7
    for class_name in [
        "hash",
        "mask",
        "redact",
        "replace",
        "encrypt",
        "custom",
        "keep",
    ]:
        assert anonymizers.get(class_name)


def test_given_decryptors_list_then_all_classes_are_there():
    decryptors = OperatorsFactory.get_deanonymizers()
    assert len(decryptors) == 1
    for class_name in ["decrypt"]:
        assert decryptors.get(class_name)


def test_given_anonymize_operators_class_then_we_get_the_correct_class():
    for operator_name in ["hash", "mask", "redact", "replace", "encrypt", "custom"]:
        operator = OperatorsFactory().create_operator_class(
            operator_name, OperatorType.Anonymize
        )
        assert operator
        assert operator.operator_name() == operator_name
        assert (
            operator.operator_type() == OperatorType.Anonymize
            or operator.operator_type() == OperatorType.All
        )


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
