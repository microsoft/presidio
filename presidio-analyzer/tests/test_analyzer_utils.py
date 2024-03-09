from presidio_analyzer import PresidioAnalyzerUtils
import pytest


@pytest.fixture(scope="module")
def recognizer():
    return PresidioAnalyzerUtils()


@pytest.fixture(scope="module")
def entities():
    return ["IN_PAN"]


palindrome_test_set = [
    ["abMA", False, False],
    ["abCba", False, True],
    ["ABBA", False, True],
    ["aBba", True, True],
    ["NotAPalindrome", True, False],
]

luhn_mod_n_test_set = [
    ["27AAACM6094R1ZP", True],
    ["36AAICA3369H1ZJ", True],
    ["36AAHAA2262Q1ZF", True],
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

iso_country_format_test_set = [
    ["ISO3166-1-Alpha-2", 249],
    ["ISO3166-1-Alpha-3", 249],
    ["ISO3166-1-Numeric", 249],
]

iso_currency_format_test_set = [
    ["ISO4217-Alpha-3", 247],
    ["ISO4217-Numeric", 246],
]

full_country_information_test_set = [
    ["Åland Islands", "English_short_name_using_title_case", 1],
    # [],
    # [],
    # [],
    # [],
    # [],
]


@pytest.mark.parametrize("input_string , expected_output", luhn_mod_n_test_set)
def test_get_luhn_mod_n(input_string, expected_output):
    """
    Test if the checksum is matching for a module-36 LUHN input
    :param input_string: string value
    :return: match if calculated checksum is same as input
    """
    assert PresidioAnalyzerUtils.get_luhn_mod_n(input_string) == expected_output


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


@pytest.mark.parametrize("iso_code, count_of_records", iso_country_format_test_set)
def test_get_country_codes(iso_code, count_of_records):
    """
    Test to get all country_codes for the given ISO format
    :param iso_code: Valid/supported ISO code
    :param count_of_records: count of total countries
    :return: list of ISO codes for all countries
    """
    pau = PresidioAnalyzerUtils()
    assert len(pau.get_country_codes(iso_code=iso_code)) == count_of_records


@pytest.mark.parametrize("iso_code, count_of_records", iso_currency_format_test_set)
def test_get_currency_codes(iso_code, count_of_records):
    """
    Test to get all country_currency_codes for the given ISO format
    :param iso_code: Valid/supported ISO code
    :param count_of_records: count of total countries
    :return: List of ISO currency codes for all countries
    """
    pau = PresidioAnalyzerUtils()
    assert len(pau.get_currency_codes(iso_code=iso_code)) == count_of_records


@pytest.mark.parametrize(
    "lookup_key, lookup_index, count_of_records", full_country_information_test_set
)
def test_get_full_country_information(lookup_key, lookup_index, count_of_records):
    pau = PresidioAnalyzerUtils()
    print(
        pau.get_full_country_information(
            lookup_key=lookup_key, lookup_index=lookup_index
        )
    )
    assert (
        len(
            pau.get_full_country_information(
                lookup_key=lookup_key, lookup_index=lookup_index
            )
        )
        == count_of_records
    )
