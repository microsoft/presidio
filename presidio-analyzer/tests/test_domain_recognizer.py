import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import DomainRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DomainRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DOMAIN_NAME"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # valid domain names
        ("microsoft.com", 1, ((0, 13),),),
        ("my domains: microsoft.com google.co.il", 2, ((12, 25), (26, 38),),),
        # invalid domain names
        ("microsoft.", 0, ()),
        ("my domain is microsoft.", 0, ()),
    ],
)
def test_all_domain_names(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, max_score)
