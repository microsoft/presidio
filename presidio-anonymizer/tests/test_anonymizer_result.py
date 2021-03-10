
from presidio_anonymizer.entities import AnonymizerResult
from presidio_anonymizer.entities.anonymized_text_index_item \
    import AnonymizedTextIndexItem


def test_when_no_params_then_object_initialised_correctly():
    res = AnonymizerResult()
    assert res.text is None
    assert res.items == []


def test_when_correct_params_then_object_initialised_correctly():
    ari = AnonymizedTextIndexItem("an", "b", 1, 2, "c")
    res = AnonymizerResult("a", [ari])
    assert res.text == "a"
    assert res.items[0] == ari


def test_when_normalized_items_called_then_idexes_are_normalized():
    ari = AnonymizedTextIndexItem("a", "b", 1, 2, "cd")
    res = AnonymizerResult("*****", [ari])
    res.normalize_item_indexes()
    assert res.items[0].start == 3
    assert res.items[0].end == 5
