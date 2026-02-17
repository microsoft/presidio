import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DeIdCardRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeIdCardRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_ID_CARD"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid ID card numbers (first char in LMNPRTVWXY, 9 chars total)
        ("L01X00T47", 1, ((0, 9),), ((0.0, 0.05),),),
        ("T22000129", 1, ((0, 9),), ((0.0, 0.05),),),
        # Invalid: first char is a vowel
        ("A01X00T47", 0, (), (),),
        # Invalid: first char is a digit
        ("101X00T47", 0, (), (),),
        # Invalid: body contains vowel
        ("L01A00T47", 0, (), (),),
        # Invalid: wrong length (too short)
        ("L01X00T4", 0, (), (),),
        # fmt: on
    ],
)
def test_when_all_de_id_cards_then_succeed(
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
