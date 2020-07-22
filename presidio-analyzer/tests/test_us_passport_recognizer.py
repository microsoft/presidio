import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import UsPassportRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return UsPassportRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["US_PASSPORT"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        ("912803456", 1, ((0, 9),), ((0.0, 0.1),),),
        # requires multiword context
        # ("my travel document is 912803456", 1, ((22, 31),), ((.5, 0.6),),),
    ],
)
def test_all_us_passports(
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
