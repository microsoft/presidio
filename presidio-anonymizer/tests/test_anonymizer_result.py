from presidio_anonymizer.entities.manipulator.manipulated_result_item import \
    ManipulatedResultItem
from presidio_anonymizer.entities.manipulator.manipulator_result import \
    ManipulatorResult


def test_when_no_params_then_object_initialised_correctly():
    res = ManipulatorResult()
    assert res.text is None
    assert res.items == []


def test_when_correct_params_then_object_initialised_correctly():
    ari = ManipulatedResultItem("an", "b", 1, 2, "c")
    res = ManipulatorResult("a", [ari])
    assert res.text == "a"
    assert res.items[0] == ari


def test_when_normalized_items_called_then_idexes_are_normalized():
    ari = ManipulatedResultItem("a", "b", 1, 2, "cd")
    res = ManipulatorResult("*****", [ari])
    res.normalize_item_indexes()
    assert res.items[0].start == 3
    assert res.items[0].end == 5


def test_when_set_text_then_text_is_set():
    res = ManipulatorResult()
    res.set_text("a")
    assert res.text == "a"


def test_when_add_item_the_item_added():
    res = ManipulatorResult()
    ari = ManipulatedResultItem("a", "b", 1, 2, "cd")
    res.add_item(ari)
    assert res.items[0] == ari


def test_when_eq_called_then_instances_are_equal():
    res = ManipulatorResult()
    res.set_text("a")
    res2 = ManipulatorResult()
    res2.set_text("a")

    assert res.__eq__(res2)


def test_when_not_eq_called_then_instances_are_not_equal():
    res = ManipulatorResult()
    res.set_text("a")
    res2 = ManipulatorResult()
    res2.set_text("b")

    assert res.__eq__(res2) is False
