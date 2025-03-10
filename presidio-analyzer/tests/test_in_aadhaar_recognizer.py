import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import InAadhaarRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return InAadhaarRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["IN_AADHAAR"]


@pytest.mark.parametrize(
    "text, expected_len, expected_position, expected_score",
    [
        # fmt: off
        ("123456789012", 0, (0,12), 0),
        ("312345678909", 1, (0, 12), 1),
        ("399876543211", 1, (0, 12), 1),
        ("My Aadhaar number is 400123456787 with a lot of text beyond it", 1, (21,33), 1),
        # fmt: on
    ],
)
def test_when_aadhaar_in_text_then_all_aadhaars_found(
    text,
    expected_len,
    expected_position,
    expected_score,
    recognizer,
    entities,
):
    results = recognizer.analyze(text, entities)
    print(results)

    assert len(results) == expected_len
    if results:
        assert_result(
            results[0],
            entities[0],
            expected_position[0],
            expected_position[1],
            expected_score,
        )

palindrome_test_set = [
    ["abMA", False, False],
    ["abCba", False, True],
    ["ABBA", False, True],
    ["aBba", True, True],
    ["NotAPalindrome", True, False],
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
            InAadhaarRecognizer._is_palindrome(input_text, case_sensitive)
            == expected_output
    )


verhoeff_test_set = [
    [312345678909, True],
    [400123456787, True],
    [123456789012, False],
]

@pytest.mark.parametrize("input_number, is_verhoeff", verhoeff_test_set)
def test_is_verhoeff(input_number, is_verhoeff):
    """
    Test to assert verhoeff number validation based on checksum from base class.

    :param input_number: input integer
    :param is_verhoeff: expected flag
    :return: True/False
    """
    assert InAadhaarRecognizer._is_verhoeff_number(input_number) == is_verhoeff
