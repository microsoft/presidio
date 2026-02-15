import pytest
from presidio_analyzer.predefined_recognizers import UkVehicleRegistrationRecognizer

from tests.assertions import assert_result_within_score_range


@pytest.fixture(scope="module")
def recognizer():
    """Create a UkVehicleRegistrationRecognizer instance."""
    return UkVehicleRegistrationRecognizer()


@pytest.fixture(scope="module")
def entities():
    """Return the list of entities to detect."""
    return ["UK_VEHICLE_REGISTRATION"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # === Current format (2001+) ===
        # Valid: standard with space
        ("AB51 ABC", 1, ((0, 8),), ((1.0, 1.0),),),
        # Valid: no space
        ("BD62XYZ", 1, ((0, 7),), ((1.0, 1.0),),),
        # Valid: with hyphen
        ("LN14-HGT", 1, ((0, 8),), ((1.0, 1.0),),),
        # Valid: lowercase (PatternRecognizer uses re.IGNORECASE)
        ("aa02 aaa", 1, ((0, 8),), ((1.0, 1.0),),),
        # Valid: embedded in text
        ("My car reg is AB51 ABC and it expires", 1, ((14, 22),), ((1.0, 1.0),),),
        # Valid: multiple in text
        (
            "Vehicles AB51 ABC and BD62XYZ were seen",
            2, ((9, 17), (22, 29),),
            ((1.0, 1.0), (1.0, 1.0),),
        ),
        # Valid: September age id (51-79)
        ("AB70 DEF", 1, ((0, 8),), ((1.0, 1.0),),),
        # Invalid: I in first area code letter
        ("IB51 ABC", 0, (), (),),
        # Invalid: Q in second area code letter
        ("AQ51 ABC", 0, (), (),),
        # Invalid: age id 00
        ("AB00 ABC", 0, (), (),),
        # Invalid: age id in gap (30-50)
        ("AB35 ABC", 0, (), (),),
        # Invalid: age id in gap (30-50)
        ("AB49 ABC", 0, (), (),),
        # Invalid: age id 80+
        ("AB80 ABC", 0, (), (),),
        # Invalid: I in random letters
        ("AB51 AIB", 0, (), (),),
        # === Prefix format (1983-2001) ===
        # Valid: standard with space
        ("A123 BCD", 1, ((0, 8),), ((0.2, 0.2),),),
        # Valid: single digit
        ("K1 ABC", 1, ((0, 6),), ((0.2, 0.2),),),
        # Valid: no space
        ("M456DEF", 1, ((0, 7),), ((0.2, 0.2),),),
        # Invalid: I as year letter
        ("I123 BCD", 0, (), (),),
        # Invalid: O as year letter
        ("O123 BCD", 0, (), (),),
        # === Suffix format (1963-1983) ===
        # Valid: standard with space
        ("ABC 123D", 1, ((0, 8),), ((0.15, 0.15),),),
        # Valid: single digit
        ("ABC 1D", 1, ((0, 6),), ((0.15, 0.15),),),
        # Valid: no spaces
        ("DEF456G", 1, ((0, 7),), ((0.15, 0.15),),),
        # Invalid: I as year suffix
        ("ABC 123I", 0, (), (),),
        # Invalid: Z as year suffix
        ("ABC 123Z", 0, (), (),),
        # === General invalid ===
        # Pure text
        ("hello world", 0, (), (),),
        # Pure digits
        ("1234567890", 0, (), (),),
        # Embedded in longer alphanumeric (no word boundary)
        ("XXXAB51ABCYYY", 0, (), (),),
        # fmt: on
    ],
)
def test_when_vehicle_reg_in_text_then_all_uk_registrations_found(  # noqa: D103
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len

    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )
