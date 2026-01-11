import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DePersonalIdRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DePersonalIdRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_PERSONAL_ID"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid new format (9 characters) with valid checksums
        ("CF0HK0K08", 1, ((0, 9),), ((0.1, 1.0),)),
        ("LM2N3P4T5", 1, ((0, 9),), ((0.1, 1.0),)),
        ("T12345679", 1, ((0, 9),), ((0.1, 1.0),)),

        # With surrounding text
        ("My ID number is CF0HK0K08 here", 1, ((16, 25),), ((0.1, 1.0),)),
        ("Personalausweis: LM2N3P4T5", 1, ((17, 26),), ((0.1, 1.0),)),

        # Multiple IDs in text
        ("IDs: CF0HK0K08 and LM2N3P4T5", 2, ((5, 14), (19, 28)), ((0.1, 1.0), (0.1, 1.0))),

        # Invalid - contains forbidden vowels (A, E, I, O, U)
        ("ABCDEFGHI", 0, (), ()),
        ("123456789A", 0, (), ()),

        # Invalid - wrong length
        ("CF0HK0K", 0, (), ()),
        ("CF0HK0K08XX", 0, (), ()),

        # Invalid - only letters or only digits of wrong length
        ("ABCDEFGHIJ", 0, (), ()),
        ("12345678", 0, (), ()),
        # fmt: on
    ],
)
def test_when_personal_id_in_text_then_all_ids_found(
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
        # Valid checksums
        ("CF0HK0K08", True),
        ("LM2N3P4T5", True),
        # Invalid checksum
        ("CF0HK0K05", False),
        # Invalid - contains vowels
        ("AEIOU1234", False),
        # Invalid - too short
        ("CF0HK0K", False),
    ],
)
def test_validate_result(text, expected, recognizer):
    """Test the validate_result method directly."""
    result = recognizer.validate_result(text)
    assert result == expected


def test_recognizer_initialization():
    """Test recognizer initialization with default parameters."""
    recognizer = DePersonalIdRecognizer()
    assert recognizer.supported_entities == ["DE_PERSONAL_ID"]
    assert recognizer.supported_language == "de"
    assert len(recognizer.patterns) == 2
    assert len(recognizer.context) > 0
