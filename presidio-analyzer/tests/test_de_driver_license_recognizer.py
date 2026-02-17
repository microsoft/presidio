import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DeDriverLicenseRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeDriverLicenseRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_DRIVER_LICENSE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid driver license numbers: [A-Z0-9]\d{2}[A-Z0-9]{6}\d[A-Z0-9]
        ("B072RRE2P90", 1, ((0, 11),), ((0.0, 0.05),),),
        ("Z99AAAAAA0A", 1, ((0, 11),), ((0.0, 0.05),),),
        ("001AAAAAA0A", 1, ((0, 11),), ((0.0, 0.05),),),
        # Invalid: wrong structure (missing digit positions)
        ("BBBRRRE2P90", 0, (), (),),
        # Invalid: wrong length (too short)
        ("B072RRE2P9", 0, (), (),),
        # Invalid: wrong length (too long)
        ("B072RRE2P900", 0, (), (),),
        # fmt: on
    ],
)
def test_when_all_de_driver_licenses_then_succeed(
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
