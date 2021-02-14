from methods import get_resource_image, compare_images
from presidio_image_anonymizer import ImageAnonymizerEngine


def test_given_image_with_text_and_fill_then_text_is_greyed_out():
    # Image with PII entities
    image = get_resource_image("ocr_test.png")
    result_image = get_resource_image("ocr_test_anonymized.png")
    anonymized_image = ImageAnonymizerEngine().anonymize(image, 1)
    assert compare_images(anonymized_image, result_image)


def test_given_image_with_text_and_matrix_fill_then_text_is_colored_out():
    # Image with PII entities
    image = get_resource_image("ocr_test.png")
    expected_result_image = get_resource_image("ocr_test_anonymized_matrix.png")
    anonymized_image = ImageAnonymizerEngine().anonymize(image, (255, 160, 122))
    assert compare_images(anonymized_image, expected_result_image)
    assert not compare_images(anonymized_image, image)


def test_given_image_without_text_and_fill_then_image_does_not_change():
    # Image without PII entities
    image = get_resource_image("no_ocr.jpg")
    anonymized_image = ImageAnonymizerEngine().anonymize(image, (255, 160, 122))
    assert compare_images(anonymized_image, image)
