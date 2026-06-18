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
        # Valid Taiwan IDs (Passing checksum algorithm verification)
        ("My ID is A123456789.", 1, ((9, 19),), ((0.2, 0.4),),),       # Valid ASCII text format
        ("A123456716", 1, ((0, 10),), ((0.2, 0.4),),),                 # Valid Checksum string
        ("身分證A123456789", 1, ((3, 13),), ((0.2, 0.4),),),            # CJK Chinese Character border check
        ("身份證字號: H123456786", 1, ((7, 17),), ((0.2, 0.4),),),        # Alternative context layout

        # Invalid Formats / Failed Checksums / Non-Matches
        ("A123456788", 0, (), (),),  # Valid formatting structure, but mathematically invalid checksum digit
        ("A323456789", 0, (), (),),  # Invalid middle format gender character
        ("A12345678", 0, (), (),),   # Insufficient length boundary
        ("a123456789", 0, (), (),),
        # Case sensitivity exclusion filter check
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

    for res, st_pos, score_range in zip(
        results, expected_positions, expected_score_ranges
    ):
        assert res.entity_type == entities[0]
        assert_result_within_score_range(
            res,
            expected_entity_type=entities[0],
            expected_start=st_pos[0],
            expected_end=st_pos[1],
            expected_score_min=score_range[0],
            expected_score_max=score_range[1],
        )
