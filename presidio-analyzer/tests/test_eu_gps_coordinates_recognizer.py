import pytest

from tests import assert_result_within_score_range
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
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # valid NIE scores
        ("48.8583° N", 1, ((0, 10),), ((0.0, 0.5),),),
        ("52.1530° N", 1, ((0, 10),), ((0.0, 0.5),),),
        ("""48°31'20" N""", 1, ((0, 11),), ((0.0, 0.5),),),
        ("""89°59'59.99" N""", 1, ((0, 14),), ((0.0, 0.5),),),
        ("13.3976° E", 1, ((0, 10),), ((0.0, 0.5),),),
        ("180°E", 1, ((0, 5),), ((0.0, 0.5),),),
        ("90°N", 1, ((0, 4),), ((0.0, 0.5),),),
        ("""13°23'53" E""", 1, ((0, 11),), ((0.0, 0.5),),),
        ("""179°59'59.99" E""", 1, ((0, 15),), ((0.0, 0.5),),),
        
    ],
)

def test_when_all_eu_gps_then_succeed(
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
