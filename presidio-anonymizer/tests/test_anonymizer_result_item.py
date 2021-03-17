import pytest

from presidio_anonymizer.entities.engine.result import AnonymizeResultItem


def test_given_anonymizer_result_item_then_all_params_exist():
    result = AnonymizeResultItem(0, 1, "t", "NAME", "replace")
    assert result.end == 1
    assert result.start == 0
    assert result.anonymized_text == "t"
    assert result.anonymizer == "replace"
    assert result.entity_type == "NAME"
    assert result.get_operated_text() == result.anonymized_text


def test_given_idenctical_anonymizer_results_item_they_are_equal():
    result_1 = AnonymizeResultItem(0, 1, "t", "NAME", "replace")
    result_2 = AnonymizeResultItem(0, 1, "t", "NAME", "replace")
    assert result_1 == result_2


@pytest.mark.parametrize(
    # fmt: off
    "result_item",
    [
        (AnonymizeResultItem(1, 1, "t", "NAME", "replace")),
        (AnonymizeResultItem(0, 2, "t", "NAME", "replace")),
        (AnonymizeResultItem(0, 1, "ta", "NAME", "replace")),
        (AnonymizeResultItem(0, 1, "t", "SNAME", "replace")),
        (AnonymizeResultItem(0, 1, "t", "NAME", "breplace")),
    ],
    # fmt: on
)
def test_given_changed_anonymizer_results_item_they_are_equal(result_item):
    result_1 = AnonymizeResultItem(0, 1, "t", "NAME", "replace")
    assert result_1 != result_item
