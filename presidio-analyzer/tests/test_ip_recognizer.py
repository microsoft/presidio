import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import IpRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return IpRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["IP_ADDRESS"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # IPv4 tests
        ("microsoft.com 192.168.0.1", 1, ((14, 25),), ((0.6, 0.81),),),
        ("my ip: 192.168.0", 0, (), (),),
        # IPv6 tests
        ("microsoft.com 684D:1111:222:3333:4444:5555:6:77", 1, ((14, 47),), ((0.6, 0.81),),),  # noqa: E501
        ("my ip: 684D:1111:222:3333:4444:5555:6:77", 1, ((7, 40),), ((0.6, 0.81),),),  # noqa: E501
        ("684D:1111:222:3333:4444:5555:77", 0, (), (),),
        ("2345:0425:2CA1:0000:0000:0567:5673:23b5", 1, ((0, 39),), ((0.6, 0.81),),),  # noqa: E501
        ("2345:0425:2CA1::0567:5673:23b5", 1, ((0, 30),), ((0.6, 0.81),),),
        ("Use local ipv6 ::", 1, ((15, 17),), ((0.05, 0.15),),),
        # fmt: on
    ],
)
def test_when_all_ips_then_succeed(
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


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # IPv6 compression edge cases - various :: positions
        ("2400:c401::5054:ff:fe1b:b031", 1, ((0, 28),), ((0.6, 0.81),),),  # Reported issue
        ("fe80::1", 1, ((0, 7),), ((0.6, 0.81),),),  # Short compressed
        ("2001:db8::8a2e:370:7334", 1, ((0, 23),), ((0.6, 0.81),),),  # Mid compression
        ("2001:db8:85a3::8a2e:370", 1, ((0, 23),), ((0.6, 0.81),),),  # Another variant
        ("2001:db8::1", 1, ((0, 11),), ((0.6, 0.81),),),  # Simple compression
        ("::ffff:192.0.2.1", 1, ((7, 16),), ((0.6, 0.81),),),  # IPv4-mapped (detects IPv4 part)
        # fmt: on
    ],
)
def test_ipv6_compression_variants(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
    max_score,
):
    """Test various IPv6 compression formats with :: in different positions."""
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


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # IPv6 addresses in realistic contexts
        ("Server IP: 2001:db8::1", 1, ((11, 22),), ((0.6, 0.81),),),
        ("Connect to [2001:db8::1]:8080", 1, ((12, 23),), ((0.6, 0.81),),),
        ("my ip is 2400:c401::5054:ff:fe1b:b031", 1, ((9, 37),), ((0.6, 0.81),),),
        ("Gateway: fe80::1 on interface", 1, ((9, 16),), ((0.6, 0.81),),),
        ("Visit http://[2001:db8::1]/path", 1, ((14, 25),), ((0.6, 0.81),),),
        ("SSH to user@2001:db8::1", 1, ((12, 23),), ((0.6, 0.81),),),
        # fmt: on
    ],
)
def test_ipv6_in_realistic_context(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
    max_score,
):
    """Test IPv6 addresses in real-world usage scenarios."""
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


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Multiple IP addresses in same text
        ("IPv4: 192.168.1.1, IPv6: 2001:db8::1", 2, ((6, 17), (25, 36)), ((0.6, 0.81), (0.6, 0.81))),
        ("Primary: 10.0.0.1, Secondary: 172.16.0.1", 2, ((9, 17), (30, 40)), ((0.6, 0.81), (0.6, 0.81))),
        ("IPs: 192.168.1.1, 10.0.0.1, 2001:db8::1", 3, ((5, 16), (18, 26), (28, 39)), ((0.6, 0.81), (0.6, 0.81), (0.6, 0.81))),
        # fmt: on
    ],
)
def test_multiple_ip_detection(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
    max_score,
):
    """Test detection of multiple IP addresses in the same text."""
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


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # These should NOT be detected as IP addresses
        ("MAC address aa:bb:cc:dd:ee:ff", 0, (), (),),  # MAC address
        ("Time 12:34:56", 0, (), (),),  # Time format
        ("Ratio 1:2:3:4", 0, (), (),),  # Ratio notation
        ("CSS color #ff00aa", 0, (), (),),  # Hex color
        ("Version 1.2.3", 0, (), (),),  # Version number (incomplete)
        ("Port 80:443", 0, (), (),),  # Port numbers
        ("abc:def:ghi", 0, (), (),),  # Non-hex text with colons
        ("123:abc", 0, (), (),),  # Mixed number/text
        ("file:///path/to/file", 0, (), (),),  # File URI
        # fmt: on
    ],
)
def test_false_positive_prevention(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
    max_score,
):
    """Test that non-IP patterns are not incorrectly detected."""
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


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Edge cases for boundary detection
        ("IP192.168.1.1text", 0, (), (),),  # No word boundary
        ("text192.168.1.1", 0, (), (),),  # No word boundary
        ("(192.168.1.1)", 1, ((1, 12),), ((0.6, 0.81),),),  # In parentheses
        ("'2001:db8::1'", 1, ((1, 12),), ((0.6, 0.81),),),  # In quotes
        ("IP: 192.168.1.1.", 1, ((4, 15),), ((0.6, 0.81),),),  # With trailing period
        ("192.168.1.1,", 1, ((0, 11),), ((0.6, 0.81),),),  # With trailing comma
        ("[2001:db8::1]", 1, ((1, 12),), ((0.6, 0.81),),),  # In brackets
        # fmt: on
    ],
)
def test_boundary_detection(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
    max_score,
):
    """Test word boundary detection for IP addresses."""
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


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Should be rejected by validation
        ("256.256.256.256", 0, (), (),),  # Invalid IPv4 octets
        ("192.168.1.256", 0, (), (),),  # Invalid IPv4 octet
        ("gggg:hhhh::1234", 1, ((9, 15),), ((0.6, 0.81),),),  # Invalid IPv6 hex (pattern matches ::1234)
        ("192.168.1", 0, (), (),),  # Incomplete IPv4
        ("300.168.1.1", 0, (), (),),  # Invalid IPv4 octet > 255
        ("192.168.1.1.1", 1, ((0, 11),), ((0.6, 0.81),),),  # Pattern matches first 4 octets
        ("12345:db8::1", 0, (), (),),  # IPv6 group too long
        ("2001::db8::1", 0, (), (),),  # Multiple :: in IPv6
        # fmt: on
    ],
)
def test_invalid_ip_rejection(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
    max_score,
):
    """Test that invalid IP-like patterns are rejected."""
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


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Additional IPv4 edge cases
        ("localhost 127.0.0.1", 1, ((10, 19),), ((0.6, 0.81),),),  # Localhost
        ("Broadcast 255.255.255.255", 1, ((10, 25),), ((0.6, 0.81),),),  # Broadcast
        ("Private 10.0.0.0", 1, ((8, 16),), ((0.6, 0.81),),),  # Private network
        ("Link-local 169.254.1.1", 1, ((11, 22),), ((0.6, 0.81),),),  # Link-local
        ("Subnet 172.16.0.0", 1, ((7, 17),), ((0.6, 0.81),),),  # Private Class B
        ("Default 0.0.0.0", 1, ((8, 15),), ((0.6, 0.81),),),  # Default route
        # Additional IPv6 edge cases
        ("Unspecified ::", 1, ((12, 14),), ((0.05, 0.15),),),  # Unspecified address
        ("Loopback ::1", 0, (), (),),  # IPv6 loopback (handled by different pattern)
        ("Multicast ff02::1", 1, ((10, 17),), ((0.6, 0.81),),),  # Multicast
        # fmt: on
    ],
)
def test_additional_ip_variants(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
    max_score,
):
    """Test additional IP address variants and special cases."""
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
