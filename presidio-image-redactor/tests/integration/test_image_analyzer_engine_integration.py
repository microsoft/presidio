from presidio_image_redactor.entities import ImageRecognizerResult
from tests.integration.methods import get_resource_image


def test_given_image_then_text_entities_are_recognized_correctly(image_analyzer_engine):
    # Image with PII entities
    image = get_resource_image("ocr_test.png")
    analyzer_results = image_analyzer_engine.analyze(image)
    assert len(analyzer_results) == 7
    results = __get_expected_ocr_test_image_analysis_results()
    for i in range(7):
        assert analyzer_results[i] == results[i]


def test_given_image_without_text_then_no_entities_recognized(image_analyzer_engine):
    # Image without PII entities
    image = get_resource_image("no_ocr.jpg")
    analyzer_results = image_analyzer_engine.analyze(image)
    assert len(analyzer_results) == 0


def __get_expected_ocr_test_image_analysis_results():
    # fmt: off
    return [
        ImageRecognizerResult(entity_type="PERSON", start=27, end=40,
                              score=0.85, left=472, top=20, width=91, height=31),
        ImageRecognizerResult(entity_type="PERSON", start=27, end=40,
                              score=0.85, left=576, top=20, width=147, height=31),
        ImageRecognizerResult(entity_type="URL", start=286, end=311,
                              score=0.6, left=28, top=299, width=438, height=38),
        ImageRecognizerResult(entity_type="PHONE_NUMBER", start=323, end=337,
                              score=0.4, left=666, top=298, width=88, height=40),
        ImageRecognizerResult(entity_type="PHONE_NUMBER", start=323, end=337,
                              score=0.4, left=769, top=301, width=169, height=29),
        ImageRecognizerResult(entity_type="EMAIL_ADDRESS", start=749, end=771,
                              score=1.0, left=27, top=912, width=458, height=39),
        ImageRecognizerResult(entity_type="URL", start=758, end=771,
                              score=0.5, left=27, top=912, width=458, height=39),
    ]
    # fmt: on
