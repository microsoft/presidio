from presidio_analyzer import PresidioAnalyzerUtils
import pytest

palindrome_test_set = [
    ["abMA", False, False],
    ["abCba", False, True],
    ["ABBA", False, True],
    ["aBba", True, True],
    ["NotAPalindrome", True, False],
]

in_vehicle_metadata_test_set = [
    ["in_non_standard_state_or_ut", 1],
    ["in_old_states", 3],
    ["in_states", 29],
    ["in_union_territories", 8],
    ["in_old_union_territories", 2],
    ["in_vehicle_dist_wb", 70],
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


def test_list_length():
    """
    Tests for static counts of each metadata lists defined
    :return: True/False
    """
    assert len(PresidioAnalyzerUtils.in_old_states) == 3
    assert len(PresidioAnalyzerUtils.in_non_standard_state_or_ut) == 1
    assert len(PresidioAnalyzerUtils.in_states) == 29
    assert len(PresidioAnalyzerUtils.in_old_union_territories) == 2
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_wb) == 97
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_up) == 85
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_uk) == 20
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_ts) == 37
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_tr) == 8
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_tn) == 98
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_sk) == 8
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_rj) == 57
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_py) == 5
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_pb) == 98
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_or) == 30
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_od) == 34
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_nl) == 10
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_mz) == 8
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_mp) == 70
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_mn) == 7
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_ml) == 10
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_mh) == 50
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_ld) == 9
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_la) == 2
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_kl) == 98
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_ka) == 70
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_jh) == 23
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_hr) == 98
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_hp) == 98
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_gj) == 39
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_ga) == 12
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_dl) == 13
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_dn) == 1
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_dd) == 3
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_ch) == 4
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_cg) == 30
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_br) == 38
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_as) == 33
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_ar) == 20
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_ap) == 2
    assert len(PresidioAnalyzerUtils.in_vehicle_dist_an) == 1
    assert len(PresidioAnalyzerUtils.in_vehicle_diplomatic_codes) == 3
    assert len(PresidioAnalyzerUtils.in_vehicle_armed_forces_codes) == 11
    assert len(PresidioAnalyzerUtils.in_vehicle_foreign_mission_codes) == 41
