import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers.country_specific.india.in_gstin_recognizer import (
    InGstinRecognizer,
)


@pytest.fixture(scope="module")
def recognizer():
    return InGstinRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["IN_GSTIN"]


@pytest.mark.parametrize(
    "text, expected_len, expected_position, expected_score",
    [
        # Valid GSTINs with high confidence
        ("27AAPFU0939F1ZV", 1, (0, 15), 1.0),
        ("07AAACR5055K1Z5", 1, (0, 15), 1.0),
        ("29AAGCB7383J1Z4", 1, (0, 15), 1.0),
        ("27AASCS2460H1Z0", 1, (0, 15), 1.0),
        # GSTIN with context
        (
            "My GSTIN number is 27AAPFU0939F1ZV for business registration",
            1,
            (19, 34),
            1.0,
        ),
        ("GST registration: 07AAACR5055K1Z5", 1, (18, 33), 1.0),
        ("Tax identification GSTIN: 29AAGCB7383J1Z4", 1, (26, 41), 1.0),
        # Multiple GSTINs
        ("GSTINs: 27AAPFU0939F1ZV and 07AAACR5055K1Z5", 2, (8, 23), 1.0),
        # Invalid GSTINs (should not be detected)
        ("27AAPFU0939F1Z", 0, (), ()),  # Too short
        ("27AAPFU0939F1ZVV", 0, (), ()),  # Too long
        ("00AAPFU0939F1ZV", 0, (), ()),  # Invalid state code
        ("38AAPFU0939F1ZV", 0, (), ()),  # Invalid state code
        ("27AAPFU0939F1YV", 0, (), ()),  # Missing 'Z' at position 14
        ("27AAPFU0939F1ZU", 0, (), ()),  # Invalid checksum
        ("27AAPFU0939F0ZV", 0, (), ()),  # Invalid registration character
    ],
)
def test_when_gstin_in_text_then_all_gstins_found(
    text,
    expected_len,
    expected_position,
    expected_score,
    recognizer,
    entities,
):
    results = recognizer.analyze(text, entities)
    
    assert len(results) == expected_len
    if results:
        assert_result(
            results[0],
            entities[0],
            expected_position[0],
            expected_position[1],
            expected_score,
        )


@pytest.mark.parametrize(
    "text, expected_len",
    [
        # Invalid formats
        ("", 0),
        ("123456789012345", 0),  # All digits
        ("ABCDEFGHIJKLMNO", 0),  # All letters
        ("27AAPFU0939F1Z", 0),  # Too short
        ("27AAPFU0939F1ZVV", 0),  # Too long
        ("00AAPFU0939F1ZV", 0),  # Invalid state code (00)
        ("38AAPFU0939F1ZV", 0),  # Invalid state code (38)
        ("27AAPFU0939F1YV", 0),  # Missing 'Z' at position 14
        ("27AAPFU0939F1Z", 0),  # Missing checksum
        ("27AAPFU0939F1ZU", 0),  # Wrong checksum
        ("27AAPFU0939F0ZV", 0),  # Invalid registration character
        ("27AAPFU0939F1ZV", 1),  # Valid GSTIN
    ],
)
def test_gstin_validation(text, expected_len, recognizer, entities):
    """Test GSTIN validation logic."""
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len


@pytest.mark.parametrize(
    "gstin, expected",
    [
        # Valid GSTINs
        ("27AAPFU0939F1ZV", True),
        ("07AAACR5055K1Z5", True),
        ("29AAGCB7383J1Z4", True),
        ("27AASCS2460H1Z0", True),
        ("27aapfu0939f1zv", True),  # Valid with different case
        # Invalid GSTINs
        ("27AAPFU0939F1Z", False),  # Too short
        ("27AAPFU0939F1ZVV", False),  # Too long
        ("00AAPFU0939F1ZV", False),  # Invalid state code
        ("38AAPFU0939F1ZV", False),  # Invalid state code
        ("27AAPFU0939F1YV", False),  # Missing 'Z' at position 14
        ("27AAPFU0939F1Z", False),  # Missing checksum
        ("27AAPFU0939F1ZU", False),  # Wrong checksum
        ("27AAPFU0939F0ZV", False),  # Invalid registration character
    ],
)
def test_validate_result(gstin, expected, recognizer):
    """Test the validate_result method directly."""
    result = recognizer.validate_result(gstin)
    assert result == expected


@pytest.mark.parametrize(
    "pan, expected",
    [
        # Valid PAN formats
        ("ABCDE1234F", True),
        ("PQRST6789K", True),
        ("ABCDE1234F", True),
        
        # Invalid PAN formats
        ("ABCD1234F", False),   # Too short
        ("ABCDE12345F", False), # Too long
        ("12345ABCDE", False),  # Numbers first
        ("ABCDE1234", False),   # Missing last letter
        ("ABCDE1234F", True),   # Valid
    ],
)
def test_validate_pan_format(pan, expected, recognizer):
    """Test PAN format validation within GSTIN."""
    result = recognizer._validate_pan_format(pan)
    assert result == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("27AAPFU0939F1ZV", "27AAPFU0939F1ZV"),
        ("27aapfu0939f1zv", "27AAPFU0939F1ZV"),
        ("27-AAPFU-0939-F1-ZV", "27AAPFU0939F1ZV"),
        ("27 AAPFU 0939 F1 ZV", "27AAPFU0939F1ZV"),
        (
            "The company GSTIN is 27AAPFU0939F1ZV for tax purposes",
            "27AAPFU0939F1ZV",
        ),
    ],
)
def test_sanitize_value(text, expected, recognizer):
    """Test value sanitization."""
    result = recognizer._sanitize_value(text)
    assert result == expected


def test_gstin_recognizer_initialization():
    """Test GSTIN recognizer initialization with default parameters."""
    recognizer = InGstinRecognizer()
    
    assert recognizer.supported_entity == "IN_GSTIN"
    assert recognizer.supported_language == "en"
    assert len(recognizer.patterns) == 3
    assert len(recognizer.context) == 6
    assert "gstin" in recognizer.context
    assert "gst" in recognizer.context


def test_gstin_recognizer_with_custom_params():
    """Test GSTIN recognizer initialization with custom parameters."""
    custom_context = ["custom", "context"]
    recognizer = InGstinRecognizer(
        context=custom_context, supported_language="hi", supported_entity="CUSTOM_GSTIN"
    )
    
    assert recognizer.supported_entity == "CUSTOM_GSTIN"
    assert recognizer.supported_language == "hi"
    assert recognizer.context == custom_context


def test_gstin_recognizer_replacement_pairs():
    """Test GSTIN recognizer with custom replacement pairs."""
    custom_replacement_pairs = [("-", ""), (" ", ""), (".", "")]
    recognizer = InGstinRecognizer(replacement_pairs=custom_replacement_pairs)
    
    assert recognizer.replacement_pairs == custom_replacement_pairs

    # Test sanitization with custom replacement pairs
    result = recognizer._sanitize_value("27-AAPFU-0939-F1-ZV")
    assert result == "27AAPFU0939F1ZV"


@pytest.mark.parametrize(
    "gstin, expected",
    [
        ("27AAPFU0939F1ZV", True),
        ("27AAPFU0939F1ZU", False),
        ("07AAACR5055K1Z5", True),
        ("07AAACR5055K1Z4", False),
    ],
)
def test_validate_checksum(gstin, expected, recognizer):
    """Test GSTIN Luhn mod-36 checksum validation."""
    assert recognizer._validate_checksum(gstin) == expected
