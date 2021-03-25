import pytest

from presidio_anonymizer.entities.engine.result import OperatorResult


def test_given_decrypt_result_item_then_all_params_exist():
    result = OperatorResult("bla", "decrypt", 0, 3, "NAME")
    assert result.end == 3
    assert result.start == 0
    assert result.text == "bla"
    assert result.entity_type == "NAME"
    assert result.operator == "decrypt"


def test_given_idenctical_decrypt_results_item_they_are_equal():
    result_1 = OperatorResult("bla", "decrypt", 0, 3, "NAME")
    result_2 = OperatorResult("bla", "decrypt", 0, 3, "NAME")
    assert result_1 == result_2


@pytest.mark.parametrize(
    # fmt: off
    "result_item",
    [
        (OperatorResult("bla1", "decrypt", 0, 3, "NAME")),
        (OperatorResult("bla", "decrypt2", 0, 3, "NAME")),
        (OperatorResult("bla", "decrypt", 1, 3, "NAME")),
        (OperatorResult("bla", "decrypt", 0, 4, "NAME")),
        (OperatorResult("bla", "decrypt", 0, 3, "1NAME")),
    ],
    # fmt: on
)
def test_given_changed_decrypt_results_item_they_are_equal(result_item):
    result_1 = OperatorResult("bla", "decrypt", 0, 3, "NAME")
    assert result_1 != result_item
