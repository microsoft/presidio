import pytest
import time
from presidio_analyzer.predefined_recognizers import PhLicensePlateRecognizer
from tests.assertions import assert_result_within_score_range


@pytest.fixture(scope="module")
def recognizer():
    """Return a PhLicensePlateRecognizer instance."""
    return PhLicensePlateRecognizer()


@pytest.fixture(scope="module")
def entities():
    """Return the PH_LICENSE_PLATE entity list."""
    return ["PH_LICENSE_PLATE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off

        # ── Modern private plates (ABC 1234) ──────────────────────────────
        # Valid: space separator
        (
            "ABC 1234",
            1,
            ((0, 8),),
            ((0.7, 0.8),),
        ),
        # Valid: dash separator
        (
            "XYZ-5678",
            1,
            ((0, 8),),
            ((0.7, 0.8),),
        ),
        # Valid: no separator
        (
            "DEF9012",
            1,
            ((0, 7),),
            ((0.7, 0.8),),
        ),
         # Valid: embedded in text
        (
            "The vehicle with plate ABC 1234 was seen near EDSA.",
            1,
            ((23, 31),),
            ((0.7, 0.8),),
        ),
        # Valid: multiple plates in one string
        (
            "Plates ABC 1234 and XYZ 5678 were flagged.",
            2,
            ((7, 15), (20, 28)),
            ((0.7, 0.8), (0.7, 0.8)),
        ),

        # ── Motorcycle plates (1234 ABC) ──────────────────────────────────
        # Valid: space separator
        (
            "4567 GHI",
            1,
            ((0, 8),),
            ((0.55, 0.65),),
        ),
        # Valid: dash separator
        (
            "9999-ZZZ",
            1,
            ((0, 8),),
            ((0.55, 0.65),),
        ),
        # Valid: no separator
        (
            "1234ABC",
            1,
            ((0, 7),),
            ((0.55, 0.65),),
        ),
        # Valid: embedded in text
        (
            "Motorcycle 4567 GHI sped away.",
            1,
            ((11, 19),),
            ((0.55, 0.65),),
        ),

        # ── Legacy private plates (AB 1234) ───────────────────────────────
        # Valid: space separator
        (
            "PQ 3456",
            1,
            ((0, 7),),
            ((0.45, 0.55),),
        ),
        # Valid: dash separator
        (
            "MN-7890",
            1,
            ((0, 7),),
            ((0.45, 0.55),),
        ),
        # Valid: embedded in text
        (
            "Old vehicle PQ 3456 still registered.",
            1,
            ((12, 19),),
            ((0.45, 0.55),),
        ),

        # ── Conduction stickers (C12D345) ─────────────────────────────────
        # Valid: standard
        (
            "C12D345",
            1,
            ((0, 7),),
            ((0.35, 0.45),),
        ),
        # Valid: longer digits
        (
            "A98B1234",
            1,
            ((0, 8),),
            ((0.35, 0.45),),
        ),
        # Valid: embedded in text
        (
            "Conduction sticker C12D345 on windshield.",
            1,
            ((19, 26),),
            ((0.35, 0.45),),
        ),

        # ── Tagalog context words ─────────────────────────────────────────
        # Valid: plaka (Tagalog for plate)
        (
            "Nakita ang plaka na ABC 1234 sa EDSA.",
            1,
            ((20, 28),),
            ((0.7, 1.0),),
        ),
        # Valid: kotse (Tagalog for car)
        (
            "Ang kotse na XYZ 5678 ay itim.",
            1,
            ((13, 21),),
            ((0.7, 1.0),),
        ),

        # ── Negative cases ────────────────────────────────────────────────
        # Invalid: all digits (zip code)
        (
            "My zip code is 90210.",
            0,
            (),
            (),
        ),
        # Invalid: lowercase letters (case-sensitive matching enforced)
        (
            "File abc 1234 not found.",
            0,
            (),
            (),
        ),
        # Invalid: empty string
        (
            "",
            0,
            (),
            (),
        ),
        # fmt: on
    ],
)
def test_when_plate_in_text_then_all_ph_plates_found(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
):
    """Test Philippine license plate detection for valid and invalid inputs."""
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )

def test_performance(recognizer, entities):
    text = ("The vehicle with plate ABC 1234 was seen near EDSA. " * 4)  # ~100 tokens
    start = time.time()
    recognizer.analyze(text, entities)
    elapsed = (time.time() - start) * 1000
    assert elapsed < 100, f"Recognizer too slow: {elapsed:.1f}ms"
