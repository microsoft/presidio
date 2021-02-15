import pytest
from presidio_anonymizer.entities import TextManipulator, InvalidParamException


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
    text_manipulator = TextManipulator(original_text)
    text_manipulator.replace_text(anonymized_text, start, end)
    assert text_manipulator.output_text == expected


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
    text_manipulator = TextManipulator(original_text)
    text_in_position = text_manipulator.validate_and_get_text_in_position(start, end)
    assert text_in_position == expected


@pytest.mark.parametrize(
    # fmt: off
    "original_text,start,end",
    [
        ("hello world", 5, 12),
        ("hello world", 12, 10),
    ],
    # fmt: on
)
def test_given_text_and_incorrect_positions_then_we_fail_to_get_text(original_text, start, end):
    text_manipulator = TextManipulator(original_text)
    err_msg = f"Invalid text position start with {start} and end with {end}, original text length is only 11."
    with pytest.raises(InvalidParamException, match=err_msg):
        text_manipulator.validate_and_get_text_in_position(start, end)
