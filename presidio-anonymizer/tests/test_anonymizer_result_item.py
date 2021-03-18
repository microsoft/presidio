import pytest

from presidio_anonymizer.entities.engine.result import AnonymizedEntity


def test_given_anonymizer_result_item_then_all_params_exist():
    result = AnonymizedEntity(0, 1, "t", "NAME", "replace")
    assert result.end == 1
    assert result.start == 0
    assert result.anonymized_text == "t"
    assert result.anonymizer == "replace"
    assert result.entity_type == "NAME"
    assert result.get_text() == result.anonymized_text


def test_given_idenctical_anonymizer_results_item_they_are_equal():
    result_1 = AnonymizedEntity(0, 1, "t", "NAME", "replace")
    result_2 = AnonymizedEntity(0, 1, "t", "NAME", "replace")
    assert result_1 == result_2


@pytest.mark.parametrize(
    # fmt: off
    "result_item",
    [
        (AnonymizedEntity(1, 1, "t", "NAME", "replace")),
        (AnonymizedEntity(0, 2, "t", "NAME", "replace")),
        (AnonymizedEntity(0, 1, "ta", "NAME", "replace")),
        (AnonymizedEntity(0, 1, "t", "SNAME", "replace")),
        (AnonymizedEntity(0, 1, "t", "NAME", "breplace")),
    ],
    # fmt: on
)
def test_given_changed_anonymizer_results_item_they_are_equal(result_item):
    result_1 = AnonymizedEntity(0, 1, "t", "NAME", "replace")
    assert result_1 != result_item
