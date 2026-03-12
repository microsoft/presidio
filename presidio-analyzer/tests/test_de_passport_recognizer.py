import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DePassportRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DePassportRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_PASSPORT"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid new format (since 2007) - starts with C, F, G, H, J, K
        # These have valid checksums
        ("C01X00T41", 1, ((0, 9),), ((0.2, 1.0),)),
        ("F2N3P4M53", 1, ((0, 9),), ((0.2, 1.0),)),
        ("G12345678", 1, ((0, 9),), ((0.2, 1.0),)),
        ("H98765433", 1, ((0, 9),), ((0.2, 1.0),)),
        ("J11223343", 1, ((0, 9),), ((0.2, 1.0),)),
        ("K55667780", 1, ((0, 9),), ((0.2, 1.0),)),

        # With surrounding text
        ("My passport is C01X00T41 here", 1, ((15, 24),), ((0.2, 1.0),)),
        # "Reisepass" rejected by validation (contains forbidden chars E, I, A, S)
        ("Reisepass: F2N3P4M53", 1, ((11, 20),), ((0.2, 1.0),)),

        # Multiple passports - "Passports" rejected (contains forbidden chars A, S, O)
        ("Passports: C01X00T41 and F2N3P4M53", 2, ((11, 20), (25, 34)), ((0.2, 1.0), (0.2, 1.0))),

        # Invalid - contain forbidden characters (A, B, D, E, I, O, Q, S, U)
        ("A12345678", 0, (), ()),  # Contains A
        ("B12345678", 0, (), ()),  # Contains B
        ("D12345678", 0, (), ()),  # Contains D

        # Wrong prefix but no forbidden chars - matches generic with low score
        ("L12345678", 1, ((0, 9),), ((0.01, 0.1),)),

        # Invalid - contains forbidden vowels
        ("CAEIOU123", 0, (), ()),

        # Invalid - wrong length
        ("C1234567", 0, (), ()),
        ("C1234567890", 0, (), ()),
        # fmt: on
    ],
)
def test_when_passport_in_text_then_all_passports_found(
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
    "text, expected",
    [
        # Valid passport with correct prefix and checksum
        ("C01X00T41", True),
        ("G12345678", True),
        # Invalid checksum
        ("C01X00T47", False),
        # Invalid - contains vowels
        ("CAEIOU123", False),
        # Invalid - wrong length
        ("C1234567", False),
        # Contains forbidden char - returns False
        ("A12345678", False),
        # Wrong prefix but no forbidden chars - returns None (could be older format)
        ("L12345678", None),
    ],
)
def test_validate_result(text, expected, recognizer):
    """Test the validate_result method directly."""
    result = recognizer.validate_result(text)
    assert result == expected


def test_recognizer_initialization():
    """Test recognizer initialization with default parameters."""
    recognizer = DePassportRecognizer()
    assert recognizer.supported_entities == ["DE_PASSPORT"]
    assert recognizer.supported_language == "de"
    assert len(recognizer.patterns) == 2
    assert len(recognizer.context) > 0
