from presidio_anonymizer.anonymizers import Anonymizer


def test_given_anonymizers_list_then_all_classes_are_there():
    anonymizers = Anonymizer.get_anonymizers()
    assert len(anonymizers) >= 5
    for class_name in ["hash", "mask", "redact", "replace"]:
        assert anonymizers.get(class_name)
