from analyzer.predefined_recognizers import NhsRecognizer

nhs_recognizer = NhsRecognizer()
entities = ["UK_NHS"]


def test_valid_uk_nhs():
    num = '401-023-2137'
    results = nhs_recognizer.analyze_all(num, entities)
    assert len(results) == 1

    num = '221 395 1837'
    results = nhs_recognizer.analyze_all(num, entities)
    assert len(results) == 1

    num = '0032698674'
    results = nhs_recognizer.analyze_all(num, entities)
    assert len(results) == 1


def test_invalid_uk_nhs():
    num = '401-023-2138'
    results = nhs_recognizer.analyze_all(num, entities)

    assert len(results) == 0
