import pytest
from presidio_anonymizer.entities import AnonymizedTextBuilder, InvalidParamException


@pytest.mark.parametrize(
    # fmt: off
    "original_text,start,end,anonymized_text,expected",
    [
        ("hello world", 0, 5, "", " world"),
        ("hello world", 5, 5, "bla", "hellobla world"),
        ("hello world", 5, 12, "bla", "hellobla"),
        ("", 5, 12, "bla", "bla"),
    ],
    # fmt: on
)
def test_given_text_then_we_replace_the_original_with_anonymized_correctly(original_text, start, end, anonymized_text,
                                                                           expected):
    text_builder = AnonymizedTextBuilder(original_text)
    text_builder.replace_text(anonymized_text, start, end)
    assert text_builder.output_text == expected


@pytest.mark.parametrize(
    # fmt: off
    "original_text,start,end,expected",
    [
        ("hello world", 0, 5, "hello"),
        ("hello world", 5, 5, ""),
        ("hello world", 6, 11, "world"),
    ],
    # fmt: on
)
def test_given_text_then_we_get_correct_indices_text_from_it(original_text, start, end, expected):
    text_builder = AnonymizedTextBuilder(original_text)
    text_in_position = text_builder.get_text_in_position(start, end)
    assert text_in_position == expected


