from presidio_analyzer import PresidioAnalyzerUtils
import pytest

palindrome_test_set = [
    ["abMA", False, False],
    ["abCba", False, True],
    ["ABBA", False, True],
    ["aBba", True, True],
    ["NotAPalindrome", True, False],
]

sanitizer_test_set = [
    ["  a|b:c       ::-", [("-", ""), (" ", ""), (":", ""), ("|", "")], "abc"],
    ["def", "", "def"],
]

verhoeff_test_set = [
    [312345678909, True],
    [400123456787, True],
    [123456789012, False],
]


@pytest.mark.parametrize(
    "input_text,case_sensitive, expected_output", palindrome_test_set
)
def test_is_palindrome(input_text, case_sensitive, expected_output):
    """
    Test if input is a true palindrome as defined in base class.

    :param input_text: input text to validate
    :param case_sensitive: flag to calculate palindrome with no case
    :param expected_output: calculated output
    :return: True/False
    """
    assert (
        PresidioAnalyzerUtils.is_palindrome(input_text, case_sensitive)
        == expected_output
    )


@pytest.mark.parametrize("input_text, params, expected_output", sanitizer_test_set)
def test_sanitize_value(input_text, params, expected_output):
    """
    Test to assert sanitize_value functionality from base class.

    :param input_text: input string
    :param params: List of tuples, indicating what has to be sanitized with which
    :param expected_output: sanitized value
    :return: True/False
    """
    assert PresidioAnalyzerUtils.sanitize_value(input_text, params) == expected_output


@pytest.mark.parametrize("input_number, is_verhoeff", verhoeff_test_set)
def test_is_verhoeff(input_number, is_verhoeff):
    """
    Test to assert verhoeff number validation based on checksum from base class.

    :param input_number: input integer
    :param is_verhoeff: expected flag
    :return: True/False
    """
    assert PresidioAnalyzerUtils.is_verhoeff_number(input_number) == is_verhoeff
