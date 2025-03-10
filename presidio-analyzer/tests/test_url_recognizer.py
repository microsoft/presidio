import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import UrlRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return UrlRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["URL"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score",
    [
        # fmt: off
        # Valid URLs
        ("https://www.microsoft.com/", 1, ((0, 26),), 0.6,),
        ("http://www.microsoft.com/", 1, ((0, 25),), 0.6,),
        ("http://www.microsoft.com", 1, ((0, 24),), 0.6,),
        ("http://microsoft.com", 1, ((0, 20),), 0.6,),
        ("http://microsoft.site", 1, ((0, 21),), 0.6,),
        ("http://microsoft.webcam", 1, ((0, 23),), 0.6,),
        ("http://microsoft.vlaanderen", 1, ((0, 27),), 0.6,),
        ("https://webhook.site/a8eedfd6-9d8a-44e0-b0fc-cc7d517db5dc?q=1&b=2", 1, ((0, 65),), 0.6,),
        ("https://www.microsoft.com/store/abc/", 1, ((0, 36),), 0.6,),
        ("microsoft.com", 1, ((0, 13),), 0.5,),
        ("my domains: microsoft.com google.co.il", 2, ((12, 25), (26, 38),), 0.5),
        ('"https://microsoft.github.io/presidio/"', 1, ((0, 39),), 0.6),  
        ("'https://microsoft.github.io/presidio/'", 1, ((0, 39),), 0.6),

        # Invalid URLs
        ("www.microsoft", 0, (), 0),
        ("http://microsoft", 0, (), 0),
        ("'www.microsoft'", 0, (), 0),
        # fmt: on
    ],
)
def test_when_all_urls_then_succeed(
        text, expected_len, expected_positions, expected_score, recognizer, entities
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, expected_score)
