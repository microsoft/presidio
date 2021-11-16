import pytest

from presidio_anonymizer.entities import OperatorResult


def test_given_decrypt_result_item_then_all_params_exist():
    result = OperatorResult(0, 3, "NAME", "bla", "decrypt")
    assert result.end == 3
    assert result.start == 0
    assert result.text == "bla"
    assert result.entity_type == "NAME"
    assert result.operator == "decrypt"


def test_given_idenctical_decrypt_results_item_they_are_equal():
    result_1 = OperatorResult(0, 3, "NAME", "bla", "decrypt")
    result_2 = OperatorResult(0, 3, "NAME", "bla", "decrypt")
    assert result_1 == result_2


@pytest.mark.parametrize(
    # fmt: off
    "result_item",
    [
        (OperatorResult(0, 3, "NAME", "bla1", "decrypt")),
        (OperatorResult(0, 3, "NAME", "bla", "decrypt2")),
        (OperatorResult(1, 3, "NAME", "bla", "decrypt")),
        (OperatorResult(0, 4, "NAME", "bla", "decrypt")),
        (OperatorResult(0, 3, "1NAME", "bla", "decrypt")),
    ],
    # fmt: on
)
def test_given_changed_decrypt_results_item_they_are_equal(result_item):
    result_1 = OperatorResult(0, 3, "NAME", "bla", "decrypt")
    assert result_1 != result_item
