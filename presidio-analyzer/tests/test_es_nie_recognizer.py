import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import EsNieRecognizer


@pytest.fixture(scope="module")
def recognizer():
    """Return an instance of the EsNieRecognizer."""
    return EsNieRecognizer()


@pytest.fixture(scope="module")
def entities():
    """Return entities to analyze."""
    return ["ES_NIE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # valid NIE scores
        ("Z8078221M", 1, ((0, 9),),),
        ("X9613851N", 1, ((0, 9),),),
        ("Y8063915Z", 1, ((0, 9),),),
        ("Y8063915-Z", 1, ((0, 10),),),
        ("Mi NIE es X9613851N", 1, ((10, 19),),),
        ("Z8078221M en mi NIE", 1, ((0, 9),),),
        ("Mi Número de identificación de extranjero es Y8063915-Z", 1, \
            ((45, 55),),),
        # invalid NIE scores
        ("Y8063915Q", 0, ()),
        ("Y806391Q", 0, ()),
        ("58063915Q", 0, ()),
        ("W8063915Q", 0, ()),
    ],
)
def test_when_all_es_nie_then_succeed(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    """Tests the ES_NIE recognizer against valid & invalid examples."""
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, max_score)
