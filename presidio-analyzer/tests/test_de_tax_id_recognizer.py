import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DeTaxIdRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeTaxIdRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_TAX_ID"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid Tax IDs (pass checksum + occurrence rule)
        ("65 929 970 489", 1, ((0, 14),), ((1.0, 1.0),),),
        ("65929970489", 1, ((0, 11),), ((1.0, 1.0),),),
        ("86 095 742 719", 1, ((0, 14),), ((1.0, 1.0),),),
        # Invalid: starts with 0
        ("02 461 357 893", 0, (), (),),
        # Invalid: bad checksum
        ("65 929 970 481", 0, (), (),),
        # Invalid: wrong length
        ("1234567890", 0, (), (),),
        ("123456789012", 0, (), (),),
        # Invalid: occurrence rule violation (all digits unique)
        ("12 345 678 903", 0, (), (),),
        # fmt: on
    ],
)
def test_when_all_de_tax_ids_then_succeed(
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
