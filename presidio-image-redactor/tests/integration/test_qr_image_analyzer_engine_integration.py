from presidio_image_redactor.entities import ImageRecognizerResult
from tests.integration.methods import get_resource_image


def test_given_qr_image_then_text_entities_are_recognized_correctly(
    qr_image_analyzer_engine,
):
    # QR image with PII entities
    image = get_resource_image("qr.png")
    analyzer_results = qr_image_analyzer_engine.analyze(image)
    assert len(analyzer_results) == 1
    assert analyzer_results[0] == ImageRecognizerResult(
        entity_type="URL",
        start=0,
        end=37,
        score=0.6,
        left=301,
        top=124,
        width=683,
        height=678,
    )


def test_given_qr_image_without_pii_then_no_entities_are_recognized(
    qr_image_analyzer_engine,
):
    # QR image without PII entities
    image = get_resource_image("qr_no_pii.png")
    analyzer_results = qr_image_analyzer_engine.analyze(image)
    assert len(analyzer_results) == 0


def test_given_mage_without_qr_then_no_entities_are_recognized(
    qr_image_analyzer_engine,
):
    # Image without QR codes
    image = get_resource_image("ocr_test.png")
    analyzer_results = qr_image_analyzer_engine.analyze(image)
    assert len(analyzer_results) == 0
