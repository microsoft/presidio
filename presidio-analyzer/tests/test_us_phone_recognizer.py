import pytest

from presidio_analyzer.predefined_recognizers import UsPhoneRecognizer
from tests import assert_result_within_score_range


@pytest.fixture(scope="module")
def recognizer():
    return UsPhoneRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["PHONE_NUMBER"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        ("(425) 882 9090", 1, ((0, 14),), ((0.7, "max"),),),
        ("my phone number is: 110bcd25-a55d-453a-8046-1297901ea002", 0, (), (),),
        ("I am available at (425) 882-9090", 1, ((18, 32),), ((0.69, "max"),),),
        ("This is just a sentence (425) 882-9090", 1, ((24, 38),), ((0.69, "max"),),),
        ("425 8829090", 1, ((0, 11),), ((0.45, 0.6),),),
        ("This is just a sentence 425 8829090", 1, ((24, 35),), ((0.29, 0.51),),),
        ("4258829090", 1, ((0, 10),), ((0.0, 0.3),),),
    ],
)
def test_all_phone_numbers(
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
