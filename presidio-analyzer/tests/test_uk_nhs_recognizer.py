import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import NhsRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return NhsRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["UK_NHS"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # fmt: off
        # valid NHS scores
        ("401-023-2137", 1, ((0, 12),),),
        ("221 395 1837", 1, ((0, 12),),),
        ("0032698674", 1, ((0, 10),),),
        # invalid NHS scores
        ("401-023-2138", 0, ()),
        # fmt: on
    ],
)
def test_when_nhs_in_text_then_all_uk_nhses_found(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, max_score)
