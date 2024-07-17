import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import NzMinistryOfHealthNumberRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return NzMinistryOfHealthNumberRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["NZ_MINISTRY_OF_HEALTH_NUMBER"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        ("GAB5261", 1, ((0, 7),), ((0.0, 0.4),),),
        ("EAE2240", 1, ((0, 7),), ((0.0, 0.4),),),
        ("AJE0437", 1, ((0, 7),), ((0.0, 0.4),),),
        
        # Invalid NZ Ministry of Health Numbers
        ("IAB5261", 0, (), (),),
        ("EAO2240", 0, (), (),),
        ("OIE0437", 0, (), (),),
        # fmt: on
    ],
)
def test_when_all_nz_ministry_health_number_found_then_succeed(
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
