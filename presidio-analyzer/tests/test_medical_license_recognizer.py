import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import MedicalLicenseRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return MedicalLicenseRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["MEDICAL_LICENSE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        ("G92341666", 1, ((0, 9),), ((0.0, 0.3),),),
        ("AA6653456", 1, ((0, 9),), ((0.0, 0.3),),),
        ("BH0450010", 1, ((0, 9),), ((0.0, 0.3),),),
        ("ZY1364061", 1, ((0, 9),), ((0.0, 0.3),),),

        # Medical License absent
        ("IA2341666", 0, (), (),),
        ("N92375416", 0, (), (),),
        # fmt: on
    ],
)
def test_when_select_medical_license_found_then_succeed(
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
