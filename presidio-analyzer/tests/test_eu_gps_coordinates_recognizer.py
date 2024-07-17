import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import EUGPSCoordinatesRecognizer


@pytest.fixture(scope="module")
def recognizer():
    """Return an instance of the EUGPSCoordinates."""
    return EUGPSCoordinatesRecognizer()


@pytest.fixture(scope="module")
def entities():
    """Return entities to analyze."""
    return ["EU_GPS_COORDINATES"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # valid NIE scores
        ("48.8583° N", 1, ((0, 10),),),
        ("52.1530° N", 1, ((0, 10),),),
        ("""48°31'20" N""", 1, ((0, 11),),),
        ("""89°59'59.99" N""", 1, ((0, 14),),),
        ("13.3976° E", 1, ((0, 10),),),
        ("180°E", 1, ((0, 5),),),
        ("90°N", 1, ((0, 4),),),
        ("""13°23'53" E""", 1, ((0, 11),),),
        ("""179°59'59.99" E""", 1, ((0, 15),),),
        
    ],
)
def test_when_all_eu_gps_then_succeed(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    """Tests the ES_NIE recognizer against valid & invalid examples."""
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, max_score)
