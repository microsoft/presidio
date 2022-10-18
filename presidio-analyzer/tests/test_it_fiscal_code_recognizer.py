import pytest

from presidio_analyzer.predefined_recognizers import ItFiscalCodeRecognizer
from tests import assert_result_within_score_range


@pytest.fixture(scope="module")
def recognizer():
    return ItFiscalCodeRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["IT_FISCAL_CODE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Test with valid Fiscal Code and valid last char
        ("AAAAAA00B11C333Y", 1, ((0, 16),), ((0.3, 1.0),),),
        # Test with valid Fiscal Code and invalid last char
        ("AAAAAA00B11C333N", 1, ((0, 16),), ((0.3, 1.0),),),
        # Test with invalid Fiscal Code
        ("AAAAAA - 00B11C333N", 0, (), (),),
        # Test with invalid Fiscal Code
        ("A55AAA00B11C333N", 0, (), (),),
        # Test with two Fiscal Code
        ("AAAAAA00B11C333Y and AAAAAA00B11C333N", 
        2,
        ((0, 16), (21, 37),),
        ((0.3, 1.0), (0.3, 1.0),),),
        # fmt: on
    ],
)
def test_when_fiscalcode_in_text_then_all_it_fiscalcode_found(
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
