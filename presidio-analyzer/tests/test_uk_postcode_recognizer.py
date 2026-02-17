import pytest

from presidio_analyzer.predefined_recognizers import UkPostcodeRecognizer
from tests.assertions import assert_result_within_score_range


@pytest.fixture(scope="module")
def recognizer():
    return UkPostcodeRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["UK_POSTCODE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Format: A9 9AA
        ("M1 1AA", 1, ((0, 6),), ((0.1, 0.1),),),
        # Format: A99 9AA
        ("M60 1NW", 1, ((0, 7),), ((0.1, 0.1),),),
        # Format: A9A 9AA
        ("W1A 1HQ", 1, ((0, 7),), ((0.1, 0.1),),),
        # Format: AA9 9AA
        ("CR2 6XH", 1, ((0, 7),), ((0.1, 0.1),),),
        # Format: AA99 9AA
        ("DN55 1PT", 1, ((0, 8),), ((0.1, 0.1),),),
        # Format: AA9A 9AA
        ("EC1A 1BB", 1, ((0, 8),), ((0.1, 0.1),),),
        # Special: GIR 0AA
        ("GIR 0AA", 1, ((0, 7),), ((0.1, 0.1),),),
        # Without space
        ("M11AA", 1, ((0, 5),), ((0.1, 0.1),),),
        ("EC1A1BB", 1, ((0, 7),), ((0.1, 0.1),),),
        ("DN551PT", 1, ((0, 7),), ((0.1, 0.1),),),
        ("GIR0AA", 1, ((0, 6),), ((0.1, 0.1),),),
        # Embedded in text
        ("My address is SW1A 1AA in London", 1, ((14, 22),), ((0.1, 0.1),),),
        ("Send to postcode EC2A 1NT please", 1, ((17, 25),), ((0.1, 0.1),),),
        # Multiple postcodes
        ("From SW1A 1AA to EC1A 1BB", 2, ((5, 13), (17, 25)), ((0.1, 0.1), (0.1, 0.1)),),  # noqa: E501
        # Invalid: Q in position 1
        ("QA1 1AA", 0, (), (),),
        # Invalid: V in position 1
        ("VA1 1AA", 0, (), (),),
        # Invalid: X in position 1
        ("XA1 1AA", 0, (), (),),
        # Invalid: C in inward code final letters
        ("M1 1CA", 0, (), (),),
        # Invalid: I in inward code final letters
        ("M1 1AI", 0, (), (),),
        # Invalid: starts with digit
        ("1A1 1AA", 0, (), (),),
        # Invalid: embedded in alphanumeric word (not at word boundary)
        ("ABCM11AADEF", 0, (), (),),
        # fmt: on
    ],
)
def test_when_postcode_in_text_then_all_uk_postcodes_found(
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
