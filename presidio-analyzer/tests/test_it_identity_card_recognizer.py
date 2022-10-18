import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import ItIdentityCardRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return ItIdentityCardRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["IT_IDENTITY_CARD"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # paper-based identity card
        (
            "AA1234567 aa 1234567",
            2,
            ((0, 9), (10, 20),),
            ((0.0, 0.05), (0.0, 0.05),),
        ),
        # CIE 2.0
        ("1234567Aa", 1, ((0, 9),), ((0.0, 0.05),),),
        # CIE 3.0
        ("AA12345aa", 1, ((0, 9),), ((0.0, 0.05),),),
        # fmt: on
    ],
)
def test_when_identity_card_in_text_then_all_it_identity_card_are_found(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
    max_score,
):
    results = recognizer.analyze(text, entities)
    results = sorted(results, key=lambda x: x.start)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        if fn_score == "max":
            fn_score = max_score
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )
