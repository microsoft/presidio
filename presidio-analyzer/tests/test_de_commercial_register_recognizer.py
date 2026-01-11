import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DeCommercialRegisterRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeCommercialRegisterRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_COMMERCIAL_REGISTER"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid HRA format (partnerships)
        ("HRA 12345", 1, ((0, 9),), ((0.4, 1.0),)),
        ("HRA12345", 1, ((0, 8),), ((0.4, 1.0),)),
        ("HRA 123456", 1, ((0, 10),), ((0.4, 1.0),)),

        # Valid HRB format (corporations)
        ("HRB 12345", 1, ((0, 9),), ((0.4, 1.0),)),
        ("HRB12345", 1, ((0, 8),), ((0.4, 1.0),)),
        ("HRB 1234567", 1, ((0, 11),), ((0.4, 1.0),)),

        # With court suffix
        ("HRB 12345 B", 1, ((0, 11),), ((0.4, 1.0),)),
        ("HRA 98765 B", 1, ((0, 11),), ((0.4, 1.0),)),

        # Case insensitive
        ("hrb 12345", 1, ((0, 9),), ((0.4, 1.0),)),
        ("hra 12345", 1, ((0, 9),), ((0.4, 1.0),)),

        # With surrounding text
        ("Registered as HRB 12345 in Munich", 1, ((14, 23),), ((0.4, 1.0),)),
        # Context pattern matches from "Handelsregister" to end
        ("Handelsregister: HRA 98765", 1, ((0, 26),), ((0.6, 1.0),)),

        # Multiple register numbers
        ("Companies: HRA 12345 and HRB 67890", 2, ((11, 20), (25, 34)), ((0.4, 1.0), (0.4, 1.0))),

        # Invalid - wrong prefix
        ("HRC 12345", 0, (), ()),
        ("HR 12345", 0, (), ()),

        # Invalid - no number
        ("HRB", 0, (), ()),
        ("HRA ABC", 0, (), ()),
        # fmt: on
    ],
)
def test_when_commercial_register_in_text_then_all_found(
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
        # Valid - contains HRA or HRB with number
        ("HRB 12345", None),  # Returns None (format only validation)
        ("HRA 98765", None),
        # Invalid - no HRA/HRB
        ("HRC 12345", False),
        # Invalid - no number
        ("HRB", False),
    ],
)
def test_validate_result(text, expected, recognizer):
    """Test the validate_result method directly."""
    result = recognizer.validate_result(text)
    assert result == expected


def test_recognizer_with_court_context(recognizer, entities):
    """Test recognition with court name context."""
    texts = [
        "HRB 12345 AG Munchen",
        "HRA 98765 Amtsgericht Berlin",
    ]
    for text in texts:
        results = recognizer.analyze(text, entities)
        assert len(results) >= 1


def test_recognizer_initialization():
    """Test recognizer initialization with default parameters."""
    recognizer = DeCommercialRegisterRecognizer()
    assert recognizer.supported_entities == ["DE_COMMERCIAL_REGISTER"]
    assert recognizer.supported_language == "de"
    assert len(recognizer.patterns) == 3
    assert len(recognizer.context) > 0
