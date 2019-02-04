from analyzer.predefined_recognizers import IbanRecognizer

iban_recognizer = IbanRecognizer()
entities = ["IBAN_CODE"]


def test_valid_iban():
    number = 'IL150120690000003111111'
    results = iban_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert results[0].score == 1


def test_invalid_iban():
    number = 'IL150120690000003111141'
    results = iban_recognizer.analyze_all(number, entities)

    assert len(results) == 0


# Context should not change the result if the checksum fails
def test_invalid_iban_with_exact_context():
    number = 'IL150120690000003111141'
    context = 'my iban number is '
    results = iban_recognizer.analyze_all(context + number, entities)

    assert len(results) == 0
