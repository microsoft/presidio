import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import VinRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return VinRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["VIN"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        ("Vehicle VIN is 1HGCM82633A004352", 1, ((15, 32),), ((0.5, "max"),)),
        ("chassis number 1HGCM82633A004352 recorded", 1, ((15, 32),), ((0.5, "max"),)),
        ("vin: 1hgcm82633a004352", 1, ((5, 22),), ((0.5, "max"),)),
        ("The vehicle identification number is 1HGCM82633A004352", 1, ((37, 54),), ((0.5, "max"),)),
        # European-style VIN with non-matching NA check digit keeps base score
        ("VIN WVWZZZ1KZAW123456 on file", 1, ((4, 21),), ((0.5, 0.5),)),
        # North American VIN with bad check digit is filtered out
        ("VIN 1HGCM82633A004353 on file", 0, (), ()),
        # Invalid cases
        ("Not a VIN: 1HGCM82633A00435", 0, (), ()),
        ("Invalid char I in 1IGCM82633A004352", 0, (), ()),
        ("Invalid char O in 1OGCM82633A004352", 0, (), ()),
        ("Invalid char Q in 1QGCM82633A004352", 0, (), ()),
        # fmt: on
    ],
)
def test_when_vin_in_text_then_detected(
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


@pytest.mark.parametrize(
    "vin, expected",
    [
        ("1HGCM82633A004352", True),
        ("WVWZZZ1KZAW123456", None),
        ("1HGCM82633A004353", False),
        ("SHORT", False),
    ],
)
def test_validate_result(vin, expected, recognizer):
    assert recognizer.validate_result(vin) is expected
