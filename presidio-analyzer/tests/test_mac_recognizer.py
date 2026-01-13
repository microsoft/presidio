import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import MacAddressRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return MacAddressRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["MAC_ADDRESS"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Colon-separated format
        ("My MAC address is 00:1A:2B:3C:4D:5E", 1, ((18, 35),), ((0.6, 0.6),)),
        ("Device MAC: AA:BB:CC:DD:EE:FF", 1, ((12, 29),), ((0.6, 0.6),)),
        ("MAC: 01:23:45:67:89:AB", 1, ((5, 22),), ((0.6, 0.6),)),
        ("Lowercase MAC: 0a:23:f5:67:89:ac", 1, ((15, 32),), ((0.6, 0.6),)),
        
        # Hyphen-separated format
        ("My MAC address is 00-1A-2B-3C-4D-5E", 1, ((18, 35),), ((0.6, 0.6),)),
        ("Hardware address: AA-BB-CC-DD-EE-FF", 1, ((18, 35),), ((0.6, 0.6),)),
        ("MAC: 01-23-45-67-89-AB", 1, ((5, 22),), ((0.6, 0.6),)),
        ("Lowercase MAC: 01-b3-4a-67-d9-cf", 1, ((15, 32),), ((0.6, 0.6),)),
        ("Mixedcase MAC: 0d-B3-4a-6A-d9-cF", 1, ((15, 32),), ((0.6, 0.6),)),
        
        # Cisco dot-separated format
        ("Cisco MAC: 0012.3456.789A", 1, ((11, 25),), ((0.6, 0.6),)),
        ("My MAC is 0012.3456.789a", 1, ((10, 24),), ((0.6, 0.6),)),
        ("Physical address is aabb.ccdd.eeff", 1, ((20, 34),), ((0.6, 0.6),)),
        
        # Multiple MAC addresses
        ("MACs: 00:11:22:33:44:55 and AA-BB-CC-DD-EE-FF", 2, ((6, 23), (28, 45)), ((0.6, 0.6), (0.6, 0.6))),
        
        # With context keywords
        ("ethernet mac address: 00:1A:2B:3C:4D:5E", 1, ((22, 39),), ((0.6, "max"),)),
        ("The hardware address is AA-BB-CC-DD-EE-FF", 1, ((24, 41),), ((0.6, "max"),)),
        
        # Invalid cases - should not match
        ("Not a MAC: 00:1A:2B:3C:4D", 0, (), ()),  # Too short
        ("Invalid: ZZ:ZZ:ZZ:ZZ:ZZ:ZZ", 0, (), ()),  # Invalid hex
        ("Broadcast: FF:FF:FF:FF:FF:FF", 0, (), ()),  # Broadcast address (filtered by invalidate_result)
        ("Invalid: 00:00:00:00:00:00", 0, (), ()),
        ("Mixed test cases for hyphens and colons: 10:2F:33-AC-29-C3", 0, (), ()),
        # fmt: on
    ],
)
def test_when_mac_addresses_then_succeed(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
    max_score,
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        if fn_score == "max":
            fn_score = max_score
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )
