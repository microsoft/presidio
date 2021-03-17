from presidio_anonymizer.operators.operators_factory import OperatorsFactory


def test_given_anonymizers_list_then_all_classes_are_there():
    anonymizers = OperatorsFactory.get_anonymizers()
    assert len(anonymizers) >= 4
    for class_name in ["hash", "mask", "redact", "replace"]:
        assert anonymizers.get(class_name)
