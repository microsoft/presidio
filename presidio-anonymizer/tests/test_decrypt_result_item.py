import pytest

from presidio_anonymizer.entities.engine.result import DecryptResultItem


def test_given_decrypt_result_item_then_all_params_exist():
    result = DecryptResultItem(0, 3, "NAME", "bla")
    assert result.end == 3
    assert result.start == 0
    assert result.decrypted_text == "bla"
    assert result.entity_type == "NAME"
    assert result.get_operated_text() == result.decrypted_text


def test_given_idenctical_decrypt_results_item_they_are_equal():
    result_1 = DecryptResultItem(0, 1, "NAME", "bla")
    result_2 = DecryptResultItem(0, 1, "NAME", "bla")
    assert result_1 == result_2


@pytest.mark.parametrize(
    # fmt: off
    "result_item",
    [
        (DecryptResultItem(1, 3, "NAME", "bla")),
        (DecryptResultItem(0, 4, "NAME", "bla")),
        (DecryptResultItem(0, 3, "NAME", "bla")),
        (DecryptResultItem(0, 3, "SNAME", "bla")),
        (DecryptResultItem(0, 3, "NAME", "bbla")),
    ],
    # fmt: on
)
def test_given_changed_decrypt_results_item_they_are_equal(result_item):
    result_1 = DecryptResultItem(0, 1, "NAME", "bla")
    assert result_1 != result_item
