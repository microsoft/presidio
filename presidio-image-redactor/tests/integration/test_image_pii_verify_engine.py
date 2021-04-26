from methods import get_resource_image, compare_images
from presidio_image_redactor import ImagePiiVerifyEngine


def test_given_image_without_text_and_pii_verify_then_image_does_not_change():
    # Image without PII entities
    image = get_resource_image("no_ocr.png")
    pii_verifying_image = ImagePiiVerifyEngine().verify(image)
    assert compare_images(pii_verifying_image, image)
