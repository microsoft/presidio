import pytest
from presidio_analyzer.predefined_recognizers import NgVehicleRegistrationRecognizer

from tests.assertions import assert_result_within_score_range


@pytest.fixture(scope="module")
def recognizer():
    """Return an NgVehicleRegistrationRecognizer instance."""
    return NgVehicleRegistrationRecognizer()


@pytest.fixture(scope="module")
def entities():
    """Return the NG_VEHICLE_REGISTRATION entity list."""
    return ["NG_VEHICLE_REGISTRATION"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid: standard format with hyphen
        (
            "APP-456CV",
            1,
            ((0, 9),),
            ((0.5, 0.5),),
        ),
        # Valid: Abuja LGA code
        (
            "ABJ-001AA",
            1,
            ((0, 9),),
            ((0.5, 0.5),),
        ),
        # Valid: high serial number
        (
            "KJA-999PZ",
            1,
            ((0, 9),),
            ((0.5, 0.5),),
        ),
        # Valid: space separator
        (
            "APP 456CV",
            1,
            ((0, 9),),
            ((0.5, 0.5),),
        ),
        # Valid: no separator
        (
            "APP456CV",
            1,
            ((0, 8),),
            ((0.5, 0.5),),
        ),
        # Valid: embedded in text
        (
            "The plate number is ABJ-123XY for this vehicle",
            1,
            ((20, 29),),
            ((0.5, 0.5),),
        ),
        # Valid: multiple in one string
        (
            "Plates: APP-456CV and KJA-999PZ",
            2,
            ((8, 17), (22, 31)),
            ((0.5, 0.5), (0.5, 0.5)),
        ),
        # Valid: lowercase (PatternRecognizer uses re.IGNORECASE by default)
        (
            "app-456cv",
            1,
            ((0, 9),),
            ((0.5, 0.5),),
        ),
        # Invalid: only 2 leading letters + 4 digits (wrong structure)
        (
            "AB-1234CD",
            0,
            (),
            (),
        ),
        # Invalid: digits where letters expected
        (
            "123-456AB",
            0,
            (),
            (),
        ),
        # Invalid: too short
        (
            "AB-12CD",
            0,
            (),
            (),
        ),
        # Invalid: too long (extra letter)
        (
            "ABCD-123EF",
            0,
            (),
            (),
        ),
        # Invalid: no match in empty text
        (
            "",
            0,
            (),
            (),
        ),
        # fmt: on
    ],
)
def test_when_vehicle_reg_in_text_then_all_ng_registrations_found(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
):
    """Test Nigerian vehicle registration detection for valid and invalid inputs."""
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len

    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )
