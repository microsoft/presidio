import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import AuMedicareRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return AuMedicareRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["AU_MEDICARE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # Valid formatting and valid Medicare number.  
        ("2123 45670 1", 1, ((0, 12),), ((1.0, 1.0),), ),
        ("2123456701", 1, ((0, 10),), ((1.0, 1.0),), ),
        # Valid formatting but invalid Medicare number.
        ("2123 25870 1", 0, (), (),),
        ("2123258701", 0, (), (),),
        # Invalid formatting and Medicare number.  
        ("212345670221", 0, (), (),),
        ("2123456702AF", 0, (), (),),
        ("123 456\n789", 0, (), (),),
    ],
)
def test_when_all_medicares_then_succeed(
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
