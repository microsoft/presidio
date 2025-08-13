import pytest

from presidio_anonymizer.entities import InvalidParamError
from presidio_anonymizer.operators import OperatorsFactory, OperatorType, AHDS_AVAILABLE


def test_given_anonymizers_list_then_all_classes_are_there():
    anonymizers = OperatorsFactory().get_anonymizers()
    expected_length = 8 if AHDS_AVAILABLE else 7
    assert len(anonymizers) == expected_length
    expected_classes = [
        "hash",
        "mask",
        "redact",
        "replace",
        "encrypt",
        "custom",
        "keep",
    ]
    if AHDS_AVAILABLE:
        expected_classes.append("surrogate_ahds")
    
    for class_name in expected_classes:
        assert anonymizers.get(class_name)


def test_given_decryptors_list_then_all_classes_are_there():
    decryptors = OperatorsFactory().get_deanonymizers()
    assert len(decryptors) == 2
    for class_name in ["decrypt"]:
        assert decryptors.get(class_name)


def test_given_anonymize_operators_class_then_we_get_the_correct_class():
    for operator_name in ["hash", "mask", "redact", "replace", "encrypt", "custom", "surrogate_ahds"]:
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
        InvalidParamError, match="Invalid operator class 'encrypt'."
    ):
        OperatorsFactory().create_operator_class("encrypt", OperatorType.Deanonymize)


def test_given_wrong_name_for_anonymizer_class_then_we_fail():
    with pytest.raises(
        InvalidParamError, match="Invalid operator class 'decrypt'."
    ):
        OperatorsFactory().create_operator_class("decrypt", OperatorType.Anonymize)


def test_given_wrong_operator_then_we_fail():
    with pytest.raises(InvalidParamError, match="Invalid operator type '3'."):
        OperatorsFactory().create_operator_class("bla", 3)


def test_given_custom_anonymizer_list_gets_updated(mock_anonymizer_cls):
    factory = OperatorsFactory()
    num_of_anonymizers = len(factory.get_anonymizers())
    factory.add_anonymize_operator(mock_anonymizer_cls)
    anonymizers = factory.get_anonymizers()
    assert len(anonymizers) == num_of_anonymizers + 1
    assert anonymizers.get("MockAnonymizer")
    assert anonymizers.get("MockAnonymizer")().operator_name() == "MockAnonymizer"


def test_given_custom_deanonymizer_list_gets_updated(mock_deanonymizer_cls):
    factory = OperatorsFactory()
    num_of_deanonymizers = len(factory.get_deanonymizers())
    factory.add_deanonymize_operator(mock_deanonymizer_cls)
    deanonymizers = factory.get_deanonymizers()
    assert len(deanonymizers) == num_of_deanonymizers + 1
    assert deanonymizers.get("MockDeanonymizer")
    assert deanonymizers.get("MockDeanonymizer")().operator_name() == "MockDeanonymizer"


def test_remove_anonymizer_removes_operator(mock_anonymizer_cls):
    factory = OperatorsFactory()
    factory.add_anonymize_operator(mock_anonymizer_cls)
    num_of_anonymizers = len(factory.get_anonymizers())
    factory.remove_anonymize_operator(mock_anonymizer_cls)
    anonymizers = factory.get_anonymizers()
    assert len(anonymizers) == num_of_anonymizers - 1
    assert not anonymizers.get("MockAnonymizer")


def test_remove_missing_anonymizer_raises_exception(mock_anonymizer_cls):
    factory = OperatorsFactory()
    with pytest.raises(
        InvalidParamError,
        match="Operator MockAnonymizer not found in anonymizers list",
    ):
        factory.remove_anonymize_operator(mock_anonymizer_cls)


def test_remove_deanonymizer_removes_operator(mock_deanonymizer_cls):
    factory = OperatorsFactory()
    factory.add_deanonymize_operator(mock_deanonymizer_cls)
    num_of_deanonymizers = len(factory.get_deanonymizers())
    factory.remove_deanonymize_operator(mock_deanonymizer_cls)
    deanonymizers = factory.get_deanonymizers()
    assert len(deanonymizers) == num_of_deanonymizers - 1


def test_remove_missing_deanonymizer_raises_exception(mock_deanonymizer_cls):
    factory = OperatorsFactory()
    with pytest.raises(
        InvalidParamError,
        match="Operator MockDeanonymizer not found in deanonymizers list",
    ):
        factory.remove_deanonymize_operator(mock_deanonymizer_cls)
