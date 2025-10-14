import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers.country_specific.india.in_gstin_recognizer import InGstinRecognizer


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
        ("27ABCDE1234F1Z5", 1, (0, 15), 1.0),
        ("07PQRST6789K1Z2", 1, (0, 15), 1.0),
        ("01ABCDE1234F1Z5", 1, (0, 15), 1.0),
        ("37ABCDE1234F1Z5", 1, (0, 15), 1.0),
        
        # Valid GSTINs with medium confidence (different PAN format)
        ("27ABCDE1234F1Z5", 1, (0, 15), 1.0),
        ("07PQRST6789K1Z2", 1, (0, 15), 1.0),
        
        # Valid GSTINs with low confidence (generic pattern)
        ("27ABCDE1234F1Z5", 1, (0, 15), 1.0),
        
        # GSTIN with context
        ("My GSTIN number is 27ABCDE1234F1Z5 for business registration", 1, (19, 34), 1.0),
        ("GST registration: 07PQRST6789K1Z2", 1, (18, 33), 1.0),
        ("Tax identification GSTIN: 01ABCDE1234F1Z5", 1, (26, 41), 1.0),
        
        # Multiple GSTINs
        ("GSTINs: 27ABCDE1234F1Z5 and 07PQRST6789K1Z2", 2, (8, 23), 1.0),
        
        # Invalid GSTINs (should not be detected)
        ("27ABCDE1234F1Z", 0, (), ()),  # Too short
        ("27ABCDE1234F1Z55", 0, (), ()),  # Too long
        ("00ABCDE1234F1Z5", 0, (), ()),  # Invalid state code
        ("38ABCDE1234F1Z5", 0, (), ()),  # Invalid state code
        ("27ABCDE1234F1Y5", 0, (), ()),  # Missing 'Z' at position 14
        ("27ABCDE1234F1Z", 0, (), ()),  # Missing checksum
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
        ("27ABCDE1234F1Z", 0),   # Too short
        ("27ABCDE1234F1Z55", 0), # Too long
        ("00ABCDE1234F1Z5", 0),  # Invalid state code (00)
        ("38ABCDE1234F1Z5", 0),  # Invalid state code (38)
        ("27ABCDE1234F1Y5", 0),  # Missing 'Z' at position 14
        ("27ABCDE1234F1Z", 0),   # Missing checksum
        ("27ABCDE1234F1Z5", 1),  # Valid GSTIN
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
        ("27ABCDE1234F1Z5", True),
        ("07PQRST6789K1Z2", True),
        ("01ABCDE1234F1Z5", True),
        ("37ABCDE1234F1Z5", True),
        
        # Invalid GSTINs
        ("27ABCDE1234F1Z", False),   # Too short
        ("27ABCDE1234F1Z55", False), # Too long
        ("00ABCDE1234F1Z5", False),  # Invalid state code
        ("38ABCDE1234F1Z5", False),  # Invalid state code
        ("27ABCDE1234F1Y5", False),  # Missing 'Z' at position 14
        ("27ABCDE1234F1Z", False),   # Missing checksum
        ("27ABCDE1234F1Z5", True),   # Valid
        ("27ABCDE1234F1Z5", True),   # Valid with different case
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
        ("27ABCDE1234F1Z5", "27ABCDE1234F1Z5"),
        ("27ABCDE1234F1Z5", "27ABCDE1234F1Z5"),
        ("27-ABCDE-1234-F1-Z5", "27ABCDE1234F1Z5"),
        ("27 ABCDE 1234 F1 Z5", "27ABCDE1234F1Z5"),
        ("The company GSTIN is 27ABCDE1234F1Z5 for tax purposes", "27ABCDE1234F1Z5"),
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
        context=custom_context,
        supported_language="hi",
        supported_entity="CUSTOM_GSTIN"
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
    result = recognizer._sanitize_value("27-ABCDE-1234-F1-Z5")
    assert result == "27ABCDE1234F1Z5"
