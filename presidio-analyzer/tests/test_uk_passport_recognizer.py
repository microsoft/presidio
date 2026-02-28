import pytest
from presidio_analyzer.predefined_recognizers import UkPassportRecognizer

from tests.assertions import assert_result_within_score_range


@pytest.fixture(scope="module")
def recognizer():
    """Create a UkPassportRecognizer instance."""
    return UkPassportRecognizer()


@pytest.fixture(scope="module")
def entities():
    """Return the list of entities to detect."""
    return ["UK_PASSPORT"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid UK passport numbers (2 letters + 7 digits)
        (
            "AB1234567",
            1,
            ((0, 9),),
            ((0.1, 0.1),),
        ),
        (
            "XY9876543",
            1,
            ((0, 9),),
            ((0.1, 0.1),),
        ),
        # Lowercase (PatternRecognizer uses re.IGNORECASE)
        (
            "ab1234567",
            1,
            ((0, 9),),
            ((0.1, 0.1),),
        ),
        # Embedded in text
        (
            "My passport number is CD7654321 and it expires soon",
            1,
            ((22, 31),),
            ((0.1, 0.1),),
        ),
        # Multiple passport numbers
        (
            "Passports: AB1234567 and XY9876543",
            2,
            (
                (11, 20),
                (25, 34),
            ),
            (
                (0.1, 0.1),
                (0.1, 0.1),
            ),
        ),
        # Invalid: 1 letter + 8 digits
        (
            "A12345678",
            0,
            (),
            (),
        ),
        # Invalid: 3 letters + 6 digits
        (
            "ABC123456",
            0,
            (),
            (),
        ),
        # Invalid: too short (2 letters + 6 digits)
        (
            "AB123456",
            0,
            (),
            (),
        ),
        # Invalid: too long (2 letters + 8 digits)
        (
            "AB12345678",
            0,
            (),
            (),
        ),
        # Invalid: 9 digits only (old format excluded)
        (
            "123456789",
            0,
            (),
            (),
        ),
        # Invalid: space in number
        (
            "AB 1234567",
            0,
            (),
            (),
        ),
        # Invalid: reversed order (digits then letters)
        (
            "1234567AB",
            0,
            (),
            (),
        ),
        # Invalid: embedded in alphanumeric word (no word boundary)
        (
            "XYZAB1234567QRS",
            0,
            (),
            (),
        ),
        # fmt: on
    ],
)
def test_when_passport_in_text_then_all_uk_passports_found(  # noqa: D103
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
