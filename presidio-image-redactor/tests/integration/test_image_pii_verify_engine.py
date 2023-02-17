from methods import get_resource_image, compare_images
from presidio_image_redactor import ImagePiiVerifyEngine


def test_given_image_without_text_and_pii_verify_then_image_does_not_change():
    # Image without PII entities
    image = get_resource_image("no_ocr.png")
    pii_verifying_image = ImagePiiVerifyEngine().verify(image)
    assert compare_images(pii_verifying_image, image)


def test_given_qr_image_with_pii_then_image_is_changed(qr_image_analyzer_engine):
    # QR image with PII entities
    image = get_resource_image("qr.png")
    result_image = get_resource_image("qr_verify.png")
    pii_verifying_image = ImagePiiVerifyEngine(image_analyzer_engine=qr_image_analyzer_engine).verify(image)
    assert compare_images(pii_verifying_image, result_image)


def test_given_qr_image_without_pii_then_image_does_not_change(qr_image_analyzer_engine):
    # QR image without PII entities
    image = get_resource_image("qr_no_pii.png")
    pii_verifying_image = ImagePiiVerifyEngine(image_analyzer_engine=qr_image_analyzer_engine).verify(image)
    assert compare_images(pii_verifying_image, image)
