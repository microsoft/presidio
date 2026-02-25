import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DeVatCodeRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeVatCodeRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_VAT_CODE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid VAT numbers (DE + 9 digits = 11 chars total)
        ("DE123456789", 1, ((0, 11),), ((0.3, 1.0),)),
        ("DE987654321", 1, ((0, 11),), ((0.3, 1.0),)),

        # With spaces (format: DE 123 456 789)
        ("DE 123 456 789", 1, ((0, 14),), ((0.4, 1.0),)),
        ("DE123 456 789", 1, ((0, 13),), ((0.4, 1.0),)),

        # With surrounding text
        ("Our VAT number is DE123456789", 1, ((18, 29),), ((0.3, 1.0),)),
        ("Umsatzsteuer-ID: DE 123 456 789", 1, ((17, 31),), ((0.4, 1.0),)),

        # Multiple VAT numbers
        ("DE123456789 and DE987654321", 2, ((0, 11), (16, 27)), ((0.3, 1.0), (0.3, 1.0))),

        # Invalid - wrong country code
        ("FR123456789", 0, (), ()),
        ("GB123456789", 0, (), ()),

        # Invalid - wrong length (10 digits instead of 9)
        ("DE1234567890", 0, (), ()),

        # Invalid - too short (8 digits instead of 9)
        ("DE12345678", 0, (), ()),

        # Invalid - contains letters after DE
        ("DEA23456789", 0, (), ()),
        # fmt: on
    ],
)
def test_when_vat_code_in_text_then_all_found(
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
        # Valid VAT format - returns None (no checksum, uses pattern score)
        ("DE123456789", None),
        ("DE987654321", None),
        # Invalid - wrong country code
        ("FR123456789", False),
        # Invalid - wrong length (10 digits)
        ("DE1234567890", False),
        # Invalid - too short (8 digits)
        ("DE12345678", False),
        # Invalid - contains letters after DE
        ("DEA23456789", False),
    ],
)
def test_validate_result(text, expected, recognizer):
    """Test the validate_result method directly."""
    result = recognizer.validate_result(text)
    assert result == expected


def test_recognizer_initialization():
    """Test recognizer initialization with default parameters."""
    recognizer = DeVatCodeRecognizer()
    assert recognizer.supported_entities == ["DE_VAT_CODE"]
    assert recognizer.supported_language == "de"
    assert len(recognizer.patterns) == 2
    assert len(recognizer.context) > 0
