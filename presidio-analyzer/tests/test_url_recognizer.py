import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import UrlRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return UrlRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["URL"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid URLs
        ("https://www.microsoft.com/", 1, ((0, 26),), ((0.6, "max"),),),
        ("http://www.microsoft.com/", 1, ((0, 25),), ((0.6, "max"),),),
        ("http://www.microsoft.com", 1, ((0, 24),), ((0.6, "max"),),),
        ("http://microsoft.com", 1, ((0, 20),), ((0.6, "max"),),),
        ("www.microsoft.com", 1, ((0, 17),), ((0.6, "max"),),),
        ("https://www.microsoft.com/store/abc/", 1, ((0, 36),), ((0.6, "max"),),),
        ("The url is www.microsoft.com", 1, ((11, 28),), ((0.6, "max"),),),
        ("microsoft.com", 1, ((0, 13),), ((0.6, "max"),),),
        # Invalid URLs
        ("www.microsoft", 0, (), ((),),),
        ("http://microsoft", 0, (), ((),),),
        # fmt: on
    ],
)
def test_when_all_urls_then_succeed(
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
