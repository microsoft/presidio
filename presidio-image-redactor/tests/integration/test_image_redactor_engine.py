from presidio_image_redactor import ImageRedactorEngine
from tests.integration.methods import get_resource_image, compare_images

red_fill = (255, 0, 0)


def test_given_image_with_text_and_fill_then_text_is_greyed_out():
    # Image with PII entities
    image = get_resource_image("ocr_test.png")
    result_image = get_resource_image("ocr_test_redacted.png")
    redacted_image = ImageRedactorEngine().redact(image, 1)
    assert compare_images(redacted_image, result_image)


def test_given_image_with_text_and_matrix_fill_then_text_is_colored_out():
    # Image with PII entities
    image = get_resource_image("ocr_test.png")

    redacted_image = ImageRedactorEngine().redact(image, red_fill)
    expected_result_image = get_resource_image("ocr_test_redacted_matrix.png")
    assert compare_images(redacted_image, expected_result_image)
    assert not compare_images(redacted_image, image)


def test_given_image_without_text_and_fill_then_image_does_not_change():
    # Image without PII entities
    image = get_resource_image("no_ocr.jpg")
    redacted_image = ImageRedactorEngine().redact(image, red_fill)
    assert compare_images(redacted_image, image)

    
def test_given_two_word_entity_then_no_extra_bounding_box_appears():
    """Tests bounding boxes for multiword entities.

    Given a PII entity is identified,
    has two or more words,
    and second word is longer than first, then:
    no extra bounding box should be created created.

    """

    # Image with two word PII entities
    image = get_resource_image("ocr_bounding_box.png")
    expected_image = get_resource_image("ocr_bounding_box_redacted.png")

    redacted_image = ImageRedactorEngine().redact(image, red_fill)
    assert compare_images(expected_image, redacted_image)
    
    
def test_given_analzyer_kwargs_then_different_entities_are_redacted():
    """
    Tests that kwargs such as entities and score_threshold are available for redact method
    """
    # Image with PII entities 
    image = get_resource_image("kwargs_test.jpg")
    redacted_image_no_args = ImageRedactorEngine().redact(image)
    redacted_image_entities_args = ImageRedactorEngine().redact(image, entities=['PERSON', 'LOCATION'])
    redacted_image_score_args = ImageRedactorEngine().redact(image, score_threshold=1)
    assert not compare_images(redacted_image_no_args, redacted_image_entities_args)
    assert not compare_images(redacted_image_no_args, redacted_image_score_args)
    assert not compare_images(redacted_image_entities_args, redacted_image_score_args)


def test_given_qr_image_with_pii_then_qr_bbox_is_redacted(qr_image_analyzer_engine):
    # QR image with PII entities
    image = get_resource_image("qr.png")
    result_image = get_resource_image("qr_redacted.png")
    redacted_image = ImageRedactorEngine(image_analyzer_engine=qr_image_analyzer_engine).redact(image)
    assert compare_images(redacted_image, result_image)


def test_given_qr_image_without_pii_then_image_does_not_change(qr_image_analyzer_engine):
    # QR image without PII entities
    image = get_resource_image("qr_no_pii.png")
    redacted_image = ImageRedactorEngine(image_analyzer_engine=qr_image_analyzer_engine).redact(image)
    assert compare_images(redacted_image, image)