import pytest
from presidio_anonymizer.entities import InvalidParamError
from presidio_anonymizer.core import TextReplaceBuilder


@pytest.mark.parametrize(
    # fmt: off
    "original_text,start,end,anonymized_text,expected,expected_end_text",
    [
        ("hello world", 0, 5, "", " world", 6),
        ("hello world", 5, 5, "bla", "hellobla world", 9),
        ("hello world", 5, 12, "bla", "hellobla", 3),
        ("The url is http://microsofy.com", 11, 31, "", "The url is ", 0)
    ],
    # fmt: on
)
def test_given_text_then_we_replace_the_original_with_anonymized_correctly(
    original_text, start, end, anonymized_text, expected, expected_end_text
):
    text_replace_builder = TextReplaceBuilder(original_text)
    end_text_num = text_replace_builder.replace_text_get_insertion_index(
        anonymized_text, start, end
    )
    assert text_replace_builder.output_text == expected
    assert expected_end_text == end_text_num


@pytest.mark.parametrize(
    # fmt: off
    "original_text,start,end,expected",
    [
        ("hello world", 0, 5, "hello"),
        ("hello world", 5, 5, ""),
        ("hello world", 6, 11, "world"),
        ("hello world", 0, 0, ""),
    ],
    # fmt: on
)
def test_given_text_then_we_get_correct_indices_text_from_it(
    original_text, start, end, expected
):
    text_replace_builder = TextReplaceBuilder(original_text)
    text_in_position = text_replace_builder.get_text_in_position(start, end)
    assert text_in_position == expected


@pytest.mark.parametrize(
    # fmt: off
    "original_text,start,end",
    [
        ("hello world", 0, 15),
        ("hello world", 12, 5),
        ("hello world", 15, 16),
    ],
    # fmt: on
)
def test_given_text_and_bad_indices_then_we_get_fail(original_text, start, end):
    text_replace_builder = TextReplaceBuilder(original_text)
    err_msg = (
        f"Invalid analyzer result, start: {start} and end: {end}, "
        f"while text length is only 11."
    )
    with pytest.raises(InvalidParamError, match=err_msg):
        text_replace_builder.get_text_in_position(start, end)
