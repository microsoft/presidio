"""Test GLiNER token truncation behavior with entities beyond 384 token limit."""
import pytest
from PIL import Image, ImageDraw, ImageFont
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_image_redactor import ImageAnalyzerEngine
from presidio_analyzer.predefined_recognizers import GLiNERRecognizer



@pytest.fixture(scope="module")
def mock_image_with_late_entities():
    """Create a test image with person names before and after the 384 token limit."""
    img = Image.new('RGB', (1000, 1400), color='white')
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    
    text_lines = [
        "Patient: Dr. Amanda Williams",
        "Doctor: Dr. James Patterson",
        "",
    ]
    
    # Add filler text to exceed 384 token limit
    text_lines.extend([
        f"Par{i}: Medical documentation regarding treatment protocols. "
        f"The facility maintains comprehensive records of consultations. "
        f"Standard procedures require detailed documentation."
        for i in range(60)
    ])
    
    # Add names beyond token limit
    text_lines.extend(["", "Nurse: Jennifer Anderson", "Therapist: Christopher Davis"])
    
    # Draw text on image
    y = 30
    for line in text_lines:
        draw.text((30, y), line, fill='black', font=font)
        y += 20
    
    return img

def extract_detected_names(results, ocr_text, expected_names):
    """Extract which expected names were detected from analyzer results."""
    detected_names = set()
    
    for result in results:
        if result.start < len(ocr_text) and result.end <= len(ocr_text):
            context = ocr_text[max(0, result.start - 20):min(len(ocr_text), result.end + 20)]
            for name in expected_names:
                if name in context or all(part in context for part in name.split()):
                    detected_names.add(name)
    
    return detected_names

def test_gliner_truncates_entities_beyond_384_tokens(mock_image_with_late_entities):
    """Test that GLiNER detects early names but misses names beyond 384 token limit."""
    # Setup analyzer with only GLiNER recognizer
    registry = RecognizerRegistry()
    registry.add_recognizer(GLiNERRecognizer())
    analyzer = AnalyzerEngine(registry=registry)
    
    # Analyze the image
    image_analyzer = ImageAnalyzerEngine(analyzer_engine=analyzer)
    results = image_analyzer.analyze(mock_image_with_late_entities)
    
    # Get OCR text for name extraction
    ocr_text = image_analyzer.ocr.get_text_from_ocr_dict(
        image_analyzer.ocr.perform_ocr(mock_image_with_late_entities)
    )
    
    # Extract detected names
    expected_names = ["Amanda Williams", "James Patterson", "Jennifer Anderson", "Christopher Davis"]
    detected_names = extract_detected_names(results, ocr_text, expected_names)
    
    for name in expected_names:
        print(f"  {'✅' if name in detected_names else '❌'} {name}")
    
    # Assert early names are detected
    assert "Amanda Williams" in detected_names, "Early name should be detected"
    assert "James Patterson" in detected_names, "Early name should be detected"
    
    # Assert late names are detected (will fail due to truncation)
    assert "Jennifer Anderson" in detected_names, "Late name missed"
    assert "Christopher Davis" in detected_names, "Late name missed"
