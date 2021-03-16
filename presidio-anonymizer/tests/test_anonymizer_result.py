from presidio_anonymizer.entities.manipulator.manipulated_result_entity import \
    ManipulatedEntity
from presidio_anonymizer.entities.manipulator.manipulated_result import \
    ManipulatedResult


def test_when_no_params_then_object_initialised_correctly():
    res = ManipulatedResult()
    assert res.text is None
    assert res.items == []


def test_when_correct_params_then_object_initialised_correctly():
    ari = ManipulatedEntity("an", "b", 1, 2, "c")
    res = ManipulatedResult("a", [ari])
    assert res.text == "a"
    assert res.items[0] == ari


def test_when_normalized_items_called_then_idexes_are_normalized():
    ari = ManipulatedEntity("a", "b", 1, 2, "cd")
    res = ManipulatedResult("*****", [ari])
    res.normalize_item_indexes()
    assert res.items[0].start == 3
    assert res.items[0].end == 5


def test_when_set_text_then_text_is_set():
    res = ManipulatedResult()
    res.set_text("a")
    assert res.text == "a"


def test_when_add_item_the_item_added():
    res = ManipulatedResult()
    ari = ManipulatedEntity("a", "b", 1, 2, "cd")
    res.add_item(ari)
    assert res.items[0] == ari


def test_when_eq_called_then_instances_are_equal():
    res = ManipulatedResult()
    res.set_text("a")
    res2 = ManipulatedResult()
    res2.set_text("a")

    assert res.__eq__(res2)


def test_when_not_eq_called_then_instances_are_not_equal():
    res = ManipulatedResult()
    res.set_text("a")
    res2 = ManipulatedResult()
    res2.set_text("b")

    assert res.__eq__(res2) is False
