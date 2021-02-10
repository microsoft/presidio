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
        # IPv6 tests  TODO IPv6 regex needs to be fixed
        # ("microsoft.com 684D:1111:222:3333:4444:5555:6:77", 1, ((14, 46),), ((0.59, 0.81),),),  # noqa: E501
        # ("my ip: 684D:1111:222:3333:4444:5555:6:77", 1, ((7, 39),), ((0.79, "max"),),),  # noqa: E501
        ("684D:1111:222:3333:4444:5555:77", 0, (), (),),
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
