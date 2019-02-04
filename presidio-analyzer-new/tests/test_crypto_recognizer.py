from analyzer.predefined_recognizers import CryptoRecognizer

crypto_recognizer = CryptoRecognizer()
entities = ["CRYPTO"]


# Generate random address https://www.bitaddress.org/


def test_valid_btc():
    wallet = '16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ'
    results = crypto_recognizer.analyze_all(wallet, entities)

    assert len(results) == 1
    assert results[0].score == 1


def test_valid_btc_with_exact_context():
    wallet = '16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ'
    context = 'my wallet address is: '
    results = crypto_recognizer.analyze_all(context + wallet, entities)

    assert len(results) == 1
    assert results[0].score == 1


def test_invalid_btc():
    wallet = '16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ2'
    results = crypto_recognizer.analyze_all('my wallet address is ' + wallet, entities)

    assert len(results) == 0
