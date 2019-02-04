from analyzer.predefined_recognizers import UsBankRecognizer

us_bank_recognizer = UsBankRecognizer()
entities = ["US_BANK_NUMBER"]


def test_us_bank_account_invalid_number():
    num = '1234567'
    results = us_bank_recognizer.analyze_all(num, entities)

    assert len(results) == 0


def test_us_bank_account_no_context():
    num = '945456787654'
    results = us_bank_recognizer.analyze_all(num, entities)

    assert len(results) == 1
    assert 0 < results[0].score < 0.1

# TODO: FIX test when context will work
# def test_us_passport_with_exact_context():
#     num = '912803456'
#     context = 'my banck account number is '
#     results = us_bank_recognizer.analyze_all(context + num, entities)
#
#     assert len(results) == 1
#     assert 0.49 < results[0].score < 0.61
#
#
# def test_us_passport_with_exact_context_no_space():
#     num = '912803456'
#     context = 'my banck account number is:'
#     results = us_bank_recognizer.analyze_all(context + num, entities)
#
#     assert len(results) == 1
#     assert 0.49 < results[0].score < 0.61
#
#
# def test_us_passport_with_lemmatized_context():
#     num = '912803456'
#     context = 'my banking account number is '
#     results = us_bank_recognizer.analyze_all(context + num, entities)
#
#     assert len(results) == 1
#     assert 0.49 < results[0].score < 0.61
