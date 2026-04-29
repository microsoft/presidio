import pytest

from presidio_analyzer.predefined_recognizers import EsPassportRecognizer
from tests.assertions import assert_result_within_score_range


@pytest.fixture(scope="module")
def recognizer():
    """Return an instance of the EsPassportRecognizer."""
    return EsPassportRecognizer()


@pytest.fixture(scope="module")
def entities():
    """Return entities to analyze."""
    return ["ES_PASSPORT"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # valid passport numbers - no context, base score only
        ("AAA123456", 1, ((0, 9),), ((0.5, 0.5),),),
        ("XYZ987654", 1, ((0, 9),), ((0.5, 0.5),),),
        # valid passport numbers - with context words, score boosted
        ("Mi pasaporte es AAA123456", 1, ((16, 25),), ((0.5, 1.0),),),
        ("AAA123456 es mi número de pasaporte", 1, ((0, 9),), ((0.5, 1.0),),),
        # invalid passport numbers
        ("AA123456", 0, (), ()),       # only 2 letters prefix
        ("AAAA12345", 0, (), ()),      # 4 letters prefix
        ("AAA12345", 0, (), ()),       # only 5 digits
        ("aaa123456", 0, (), ()),      # lowercase letters
    ],
)
def test_when_all_es_passport_then_succeed(
    text, expected_len, expected_positions, expected_score_ranges, recognizer, entities
):
    """Tests the ES_PASSPORT recognizer against valid & invalid examples."""
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )
