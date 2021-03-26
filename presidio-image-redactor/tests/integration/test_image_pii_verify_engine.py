from methods import get_resource_image, compare_images
from presidio_image_redactor import ImagePiiVerifyEngine

def test_given_image_without_text_and_pii_verify_then_image_does_not_change():
    # Image without PII entities
    image = get_resource_image("no_ocr.png")
    pii_verifying_image = ImagePiiVerifyEngine().verify(image)
    assert compare_images(pii_verifying_image, image)
def test_given_image_with_text_and_Pii_is_shown():
    # Image with PII entities
    image = get_resource_image("ocr_test.png")
    pii_verifying_image = ImagePiiVerifyEngine().verify(image)

    expected_result_image = get_resource_image("pii_verify.png")
    assert compare_images(pii_verifying_image, expected_result_image)
    assert not compare_images(pii_verifying_image, image)    