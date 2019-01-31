from tests import CreditCardRecognizer

# https://www.datatrans.ch/showcase/test-cc-numbers
# https://www.freeformatter.com/credit-card-number-generator-validator.html

def test_valid_credit_cards():
    # init
    credit_card_recognizer = CreditCardRecognizer()

    number1 = '4012888888881881'
    number2 = '4012-8888-8888-1881'
    number3 = '4012 8888 8888 1881'

    results = credit_card_recognizer.analyze_all('{} {} {}'.format(number1, number2, number3), ["CREDIT_CARD"])

    assert len(results) == 3
    assert results[0].entity_type == "CREDIT_CARD"
    assert results[0].score == 1.0
    assert results[1].score == 1.0
    assert results[2].score == 1.0
