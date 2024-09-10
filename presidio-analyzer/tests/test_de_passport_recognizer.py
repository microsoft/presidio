import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DePassportRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DePassportRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_PASSPORT_NUMBER"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        ("GLV7005V0d", 1, ((0, 10),), ((0.0, 0.4),),),
        ("JT4NRZ8PMd", 1, ((0, 10),), ((0.0, 0.4),),),
        ("FRRJNYXKM1d", 1, ((0, 11),), ((0.0, 0.4),),),
        ("JW3TV1WNX0d", 1, ((0, 11),), ((0.0, 0.4),),),
        # fmt: on
    ],
)
def test_when_passport_in_text_then_all_de_passports_found(
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
