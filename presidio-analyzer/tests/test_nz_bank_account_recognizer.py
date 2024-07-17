import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import NzBankAccountRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return NzBankAccountRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["NZ_BANK_ACCOUNT_NUMBER"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        ("12345344455594", 1, ((0, 14),), ((0.0, 0.4),),),
        ("12-345-3444555-94", 1, ((0, 17),), ((0.0, 0.4),),),
        ("12-3453-4445559-49", 1, ((0, 18),), ((0.0, 0.4),),),
        ("12-345-3444555-940", 1, ((0, 18),), ((0.0, 0.4),),),
        # fmt: on
    ],
)
def test_when_all_nz_bank_account_number_found_then_succeed(
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
