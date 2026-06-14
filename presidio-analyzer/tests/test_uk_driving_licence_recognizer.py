import pytest

from presidio_analyzer.predefined_recognizers import UkDrivingLicenceRecognizer
from tests.assertions import assert_result_within_score_range


@pytest.fixture(scope="module")
def recognizer():
    return UkDrivingLicenceRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["UK_DRIVING_LICENCE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Male licence (Morgan, born 05/07/1965, initials S M)
        ("MORGA607054SM9IJ", 1, ((0, 16),), ((0.3, 0.5),),),
        # Female licence (month + 50 = 57 for July)
        ("MORGA657054SM9IJ", 1, ((0, 16),), ((0.3, 0.5),),),
        # Padded surname (short name "FO" -> FO999)
        ("FO999512018AA1AB", 1, ((0, 16),), ((0.3, 0.5),),),
        # Single-char surname padding (name "SMIT" -> SMIT9)
        ("SMIT9801015JK2CD", 1, ((0, 16),), ((0.3, 0.5),),),
        # Embedded in text
        ("Licence: MORGA607054SM9IJ ok", 1, ((9, 25),), ((0.3, 0.5),),),
        # Lowercase input (PatternRecognizer uses case-insensitive matching)
        ("morga607054sm9ij", 1, ((0, 16),), ((0.3, 0.5),),),
        # Initials with 9 (no middle initial)
        ("JONES710153J99EF", 1, ((0, 16),), ((0.3, 0.5),),),
        # February 29 (valid day)
        ("SMITH802290AB1CD", 1, ((0, 16),), ((0.3, 0.5),),),
        # Month 12 (December, male)
        ("SMITH812310AB1CD", 1, ((0, 16),), ((0.3, 0.5),),),
        # Month 51 (January, female)
        ("SMITH851010AB1CD", 1, ((0, 16),), ((0.3, 0.5),),),
        # Month 62 (December, female)
        ("SMITH862310AB1CD", 1, ((0, 16),), ((0.3, 0.5),),),
        # fmt: on
    ],
)
def test_valid_uk_driving_licences(
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


@pytest.mark.parametrize(
    "text",
    [
        # Invalid month 00
        "MORGA600054SM9IJ",
        # Invalid month 13
        "MORGA613054SM9IJ",
        # Invalid month 50
        "MORGA650054SM9IJ",
        # Invalid month 63
        "MORGA663054SM9IJ",
        # Invalid day 00
        "MORGA601004SM9IJ",
        # Invalid day 32
        "MORGA601324SM9IJ",
        # Wrong length (15 characters)
        "MORGA65705SM9IJ",
        # Wrong length (17 characters)
        "MORGA6570544SM9IJ",
        # All 9s surname
        "99999657054SM9IJ",
        # Surname with 9 before letter (invalid padding)
        "MO9G9657054SM9IJ",
    ],
)
def test_invalid_uk_driving_licences(text, recognizer, entities):
    results = recognizer.analyze(text, entities)
    assert len(results) == 0
