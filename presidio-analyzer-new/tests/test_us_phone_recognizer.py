from analyzer.predefined_recognizers import UsPhoneRecognizer

phone_recognizer = UsPhoneRecognizer()
entities = ["PHONE_NUMBER"]


def test_phone_number_strong_match_no_context():
    number = '(425) 882 9090'
    results = phone_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert 0.69 < results[0].score < 1

# TODO: enable when context is working
# def test_phone_number_strong_match_with_phone_context():
#     number = '(425) 882-9090'
#     context = 'my phone number is '
#     results = phone_recognizer.analyze_all(context + number, entities)
#
#     assert len(results) == 1
#     assert results[0].score == 1
#
#
# def test_phone_number_strong_match_with_phone_context_no_space():
#     number = '(425) 882-9090'
#     context = 'my phone number is:'
#     results = phone_recognizer.analyze_all(context + number, entities)
#
#     assert len(results) == 1
#     assert results[0].score == 1


def test_phone_in_guid():
    number = '110bcd25-a55d-453a-8046-1297901ea002'
    context = 'my phone number is:'
    results = phone_recognizer.analyze_all(context + number, entities)

    assert len(results) == 0


def test_phone_number_strong_match_with_similar_context():
    number = '(425) 882-9090'
    context = 'I am available at '
    results = phone_recognizer.analyze_all(context + number, entities)

    assert len(results) == 1
    assert results[0].score > 0.69


def test_phone_number_strong_match_with_irrelevant_context():
    number = '(425) 882-9090'
    context = 'This is just a sentence '
    results = phone_recognizer.analyze_all(context + number, entities)

    assert len(results) == 1
    assert 0.69 < results[0].score < 1


def test_phone_number_medium_match_no_context():
    number = '425 8829090'
    results = phone_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert 0.45 < results[0].score < 0.6

# TODO: enable when context works
# def test_phone_number_medium_match_with_phone_context():
#     number = '425 8829090'
#     context = 'my phone number is '
#     results = phone_recognizer.analyze_all(context + number, entities)
#
#     assert len(results) == 1
#     assert 0.75 < results[0].score < 0.9
#
#
# def test_phone_number_weak_match_with_phone_context():
#     number = '4258829090'
#     context = 'my phone number is '
#     results = phone_recognizer.analyze_all(context + number, entities)
#
#     assert len(results) == 1
#     assert 0.59 < results[0].score < 0.81
#
#
# def test_phone_numbers_lemmatized_context_phones():
#     number1 = '052 5552606'
#     number2 = '074-7111234'
#     results = phone_recognizer.analyze_all(
#         'try one of these phones ' + number1 + ' ' + number2, entities)
#
#     assert len(results) == 2
#     assert 0.75 < results[0].score < 0.9
#     assert 0.75 < results[0].score < 0.9

''' This test fails since available is not close enough to phone --> requires experimentation with language model

def test_phone_number_medium_match_with_similar_context():
    number = '425 8829090'
    context = 'I am available at '
    results = phone_recognizer.analyze_all(context + number, entities)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].score > 0.59 and results[0].score < 0.8
'''


def test_phone_number_medium_match_with_irrelevant_context():
    number = '425 8829090'
    context = 'This is just a sentence '
    results = phone_recognizer.analyze_all(context + number, entities)

    assert len(results) == 1
    assert 0.29 < results[0].score < 0.51


def test_phone_number_weak_match_no_context():

    number = '4258829090'
    results = phone_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert 0 < results[0].score < 0.3



