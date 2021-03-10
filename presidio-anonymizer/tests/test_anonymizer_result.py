
from presidio_anonymizer.entities import AnonymizerResult
from presidio_anonymizer.entities.anonymizer_result_item import AnonymizerResultItem


def test_when_no_params_then_object_initialised_correctly():
    res = AnonymizerResult()
    assert res.text is None
    assert res.items == []


def test_when_correct_params_then_object_initialised_correctly():
    ari = AnonymizerResultItem("an", "b", 1, 2, "c")
    res = AnonymizerResult("a", [ari])
    assert res.text == "a"
    assert res.items[0] == ari


def test_when_normalized_items_called_then_idexes_are_normalized():
    ari = AnonymizerResultItem("a", "b", 1, 2, "cd")
    res = AnonymizerResult("*****", [ari])
    res.normalize_item_indexes()
    assert res.items[0].start == 3
    assert res.items[0].end == 5
