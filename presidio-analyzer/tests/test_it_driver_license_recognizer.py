import pytest

from presidio_analyzer.predefined_recognizers import ItDriverLicenseRecognizer
from tests import assert_result_within_score_range


@pytest.fixture(scope="module")
def recognizer():
    return ItDriverLicenseRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["IT_DRIVER_LICENSE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Test with one Driver License
        ("AA0123456B", 1, ((0, 10),), ((0.1, 0.4),),),
        # Test with two Driver License
        ("AA0123456B and AA0123456B", 
        2,
        ((0, 10), (15, 25),),
        ((0.1, 0.4), (0.1, 0.4),),),
        # Test with old Driver License
        ("U1H00A000B", 1, ((0, 10),), ((0.1, 0.4),),),
        # Test with invalid Driver License
        ("990123456B", 0, (), (),),
        # fmt: on
    ],
)
def test_when_driver_licenses_in_text_then_all_it_driver_licenses_found(
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
