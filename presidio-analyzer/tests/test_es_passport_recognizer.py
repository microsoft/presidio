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
        ("AAA123456", 1, ((0, 9),), ((0.05, 0.05),),),
        ("XYZ987654", 1, ((0, 9),), ((0.05, 0.05),),),
        # valid passport numbers - with context words, score boosted
        ("Mi pasaporte es AAA123456", 1, ((16, 25),), ((0.05, 1.0),),),
        ("AAA123456 es mi número de pasaporte", 1, ((0, 9),), ((0.05, 1.0),),),
        # valid passport numbers - no context, base score only - lowercase letters  
        ("aaa123456", 1, ((0, 9),), ((0.05, 0.05),),),
        ("xyz987654", 1, ((0, 9),), ((0.05, 0.05),),),
        # valid passport numbers - with context words, score boosted  - lowercase letters  
        ("Mi pasaporte es aaa123456", 1, ((16, 25),), ((0.05, 1.0),),),
        ("aaa123456 es mi número de pasaporte", 1, ((0, 9),), ((0.05, 1.0),),),
        # valid passport numbers - no context, base score only - case mixed letters
        ("AaA123456", 1, ((0, 9),), ((0.05, 0.05),),),
        ("XyZ987654", 1, ((0, 9),), ((0.05, 0.05),),),
        # valid passport numbers - with context words, score boosted  - case mixed letters
        ("Mi pasaporte es AaA123456", 1, ((16, 25),), ((0.05, 1.0),),),
        ("AaA123456 es mi número de pasaporte", 1, ((0, 9),), ((0.05, 1.0),),),
        # invalid passport numbers
        ("AA123456", 0, (), ()),       # only 2 letters prefix
        ("AAAA12345", 0, (), ()),      # 4 letters prefix
        ("AAA12345", 0, (), ()),       # only 5 digits
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
