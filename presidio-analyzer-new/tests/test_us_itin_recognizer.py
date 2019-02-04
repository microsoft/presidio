from analyzer.predefined_recognizers import UsItinRecognizer
import os

us_itin_recognizer = UsItinRecognizer()
entities = ["US_ITIN"]


def test_valid_us_itin_very_weak_match():
    num1 = '911-701234'
    num2 = '91170-1234'
    results = us_itin_recognizer.analyze_all('{} {}'.format(num1, num2), entities)

    assert len(results) == 2
    assert 0 < results[0].score < 0.31
    assert results[1].score > 0 and results[0].score < 0.31


def test_valid_us_itin_weak_match():
    num = '911701234'
    results = us_itin_recognizer.analyze_all(num, entities)

    assert len(results) == 1
    assert 0.29 < results[0].score < 0.41


def test_valid_us_itin_medium_match():
    num = '911-70-1234'
    results = us_itin_recognizer.analyze_all(num, entities)

    assert len(results) == 1
    assert 0.49 < results[0].score < 0.6

# TODO: enable when context is working
# def test_valid_us_itin_very_weak_match_exact_context():
#     num1 = '911-701234'
#     num2 = '91170-1234'
#     context = "my taxpayer id is"
#     results = us_itin_recognizer.analyze_all('{} {} {}'.format(context, num1, num2), entities)
#
#     assert len(results) == 2
#     assert 0.59 < results[0].score < 0.7
#     assert 0.50 < results[1].score < 0.7
#
#
# def test_valid_us_itin_weak_match_exact_context():
#     num = '911701234'
#     context = "my itin:"
#     results = us_itin_recognizer.analyze_all('{} {}'.format(context, num), entities)
#
#     assert len(results) == 1
#     assert 0.5 < results[0].score < 0.65
#
#
# def test_valid_us_itin_medium_match_exact_context():
#     num = '911-70-1234'
#     context = "my itin is"
#     results = us_itin_recognizer.analyze_all('{} {}'.format(context, num), entities)
#
#     assert len(results) == 1
#     assert 0.6 < results[0].score < 0.9


def test_invalid_us_itin():
    num = '911-89-1234'
    results = us_itin_recognizer.analyze_all(num, entities)

    assert len(results) == 0


def test_invalid_us_itin_exact_context():
    num = '911-89-1234'
    context = "my taxpayer id"
    results = us_itin_recognizer.analyze_all('{} {}'.format(context, num), entities)

    assert len(results) == 0

