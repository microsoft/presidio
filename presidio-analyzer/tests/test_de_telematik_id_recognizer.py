import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DeTelematikIdRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeTelematikIdRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_TELEMATIK_ID"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid Telematik-ID formats

        # Healthcare professional (eHBA) - prefix 1-
        ("1-10000100001111", 1, ((0, 16),), ((0.4, 1.0),)),
        ("eHBA: 1-ABCD123.456", 1, ((6, 19),), ((0.4, 1.0),)),

        # Patient Gesundheits-ID - prefix 10- (CRITICAL since 2026)
        ("10-ABC123XYZ789", 1, ((0, 15),), ((0.4, 1.0),)),
        ("Gesundheits-ID: 10-12345.67890", 1, ((16, 30),), ((0.4, 1.0),)),
        ("Patient ID 10-HEALTH123456", 1, ((11, 26),), ((0.4, 1.0),)),

        # Hospital institution (SMC-B) - prefix 5-2-
        ("5-2-123456789012", 1, ((0, 16),), ((0.3, 1.0),)),

        # Multiple IDs in text
        ("eHBA 1-ABC123 und Gesundheits-ID 10-XYZ789", 2, ((5, 13), (33, 42)), ((0.4, 1.0), (0.4, 1.0))),

        # With context
        ("Telematik-ID: 1-DOC123456", 1, ((14, 25),), ((0.4, 1.0),)),
        ("E-Rezept ID 10-PATIENT789", 1, ((12, 25),), ((0.4, 1.0),)),

        # Invalid - too short
        ("1-AB", 0, (), ()),

        # Invalid - no valid prefix
        ("99-123456789", 0, (), ()),

        # Text with invalid chars - regex stops at valid portion, matches 1-ABCDEF (8 chars)
        ("1-ABCDEF@#$%", 1, ((0, 8),), ((0.4, 1.0),)),
        # fmt: on
    ],
)
def test_when_telematik_id_in_text_then_all_found(
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
        # Valid formats - return None to use pattern score
        ("1-10000100001111", None),  # Healthcare professional
        ("10-ABC123XYZ789", None),  # Patient Gesundheits-ID
        ("5-2-123456789012", None),  # Hospital
        ("1-ABCDEF", None),  # Short but valid

        # Invalid - too short (less than 7 chars total)
        ("1-AB", False),
        ("1-ABC", False),

        # Invalid - wrong prefix
        ("99-123456789", False),

        # Invalid - invalid characters (contains @#$%)
        ("1-ABCD@#$%", False),

        # Invalid - too long (> 128 chars)
        ("1-" + "A" * 130, False),
    ],
)
def test_validate_result(text, expected, recognizer):
    """Test the validate_result method directly."""
    result = recognizer.validate_result(text)
    assert result == expected


def test_recognizer_initialization():
    """Test recognizer initialization with default parameters."""
    recognizer = DeTelematikIdRecognizer()
    assert recognizer.supported_entities == ["DE_TELEMATIK_ID"]
    assert recognizer.supported_language == "de"
    assert len(recognizer.patterns) == 3
    assert len(recognizer.context) > 0
