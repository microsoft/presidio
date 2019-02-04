from analyzer.predefined_recognizers import UsPassportRecognizer

us_passport_recognizer = UsPassportRecognizer()
entities = ["US_PASSPORT"]


def test_valid_us_passport_no_context():
    num = '912803456'
    results = us_passport_recognizer.analyze_all(num, entities)

    assert len(results) == 1
    assert 0 < results[0].score < 0.1

# TODO: enable when context is working
# def test_valid_us_passport_with_exact_context():
#     num = '912803456'
#     context = 'my passport number is '
#     results = us_passport_recognizer.analyze_all(context + num, entities)
#
#     assert len(results) == 1
#     assert 0.49 < results[0].score < 0.71
    ''' Should pass after handling keyphrases, e.g. "travel document" or "travel permit"

    def test_valid_us_passport_with_exact_context_phrase():
    num = '912803456'
    context = 'my travel document number is '
    results = us_passport_recognizer.analyze_all(context + num, entities)

    assert len(results) == 1
    assert results[0].text = num
    assert results[0].score
    '''
