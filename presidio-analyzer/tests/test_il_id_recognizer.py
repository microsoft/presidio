from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import ILIDRecognizer

il_id_recognizer = ILIDRecognizer()
entities = ["IL_ID"]


def test_valid_il_id_match():
    num1 = '012345678'
    num2 = '01234567'
    results = il_id_recognizer.analyze(
        '{} {}'.format(num1, num2), entities)

    assert len(results) == 2

    print(results[0])
    print(results[1])
    assert results[0].score != 0
    assert_result_within_score_range(
        results[0], entities[0], 0, 9, 0, 0.3)

    assert results[1].score != 0
    assert_result_within_score_range(
        results[1], entities[0], 10, 18, 0, 0.3)

def test_invalid_long_il_id():
    num = '012345678901234567890'
    results = il_id_recognizer.analyze(num, entities)

    assert len(results) == 0

def test_invalid_short_il_id():
    num = '0123'
    results = il_id_recognizer.analyze(num, entities)

    assert len(results) == 0

def test_invalid_il_id():
    num = '0-1-2-3-4-5-6'
    results = il_id_recognizer.analyze(num, entities)

    assert len(results) == 0
