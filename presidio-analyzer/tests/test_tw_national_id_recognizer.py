import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import TwNationalIdRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return TwNationalIdRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["TW_NATIONAL_ID"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid Taiwan IDs (Citizen Male, Citizen Female, Resident Male, Resident Female)
        ("My ID is A123456789.", 1, ((9, 19),), ((0.2, 0.4),),),
        ("B298765432", 1, ((0, 10),), ((0.2, 0.4),),),
        ("F800000014", 1, ((0, 10),), ((0.2, 0.4),),),
        ("H987654321", 1, ((0, 10),), ((0.2, 0.4),),),
        
        # Invalid Formats / Non-Matches
        ("A323456789", 0, (), (),),  # Invalid starting digit (3 is not a valid gender code)
        ("A12345678", 0, (), (),),   # Too short (only 8 digits)
        ("A1234567890", 0, (), (),), # Too long (10 digits)
        ("1123456789", 0, (), (),),  # Missing leading character letter
        ("a123456789", 0, (), (),),  # Lowercase character letter
        # fmt: on
    ],
)
def test_when_tw_national_id_in_text_then_all_are_found(
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
