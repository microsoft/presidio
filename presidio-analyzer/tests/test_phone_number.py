from analyzer import matcher, common_pb2
from tests import *

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.PHONE_NUMBER)
types = [fieldType]

def test_phone_number_strong_match_no_context():
    number = '(425) 882 9090'
    results = match.analyze_text(number, types)
    
    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability > 0.69 and results[0].probability < 1


def test_phone_number_strong_match_with_phone_context():
    number = '(425) 882-9090'
    context = 'my phone number is '
    results = match.analyze_text(context + number, types)
    
    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1


def test_phone_number_strong_match_with_similar_context():
    number = '(425) 882-9090'
    context = 'I am available at '
    results = match.analyze_text(context + number, types)
    
    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability > 0.69 


def test_phone_number_strong_match_with_irrelevant_context():
    number = '(425) 882-9090'
    context = 'This is just a sentence '
    results = match.analyze_text(context + number, types)
    
    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability > 0.69 and results[0].probability < 1

def test_phone_number_medium_match_no_context():
    number = '425 8829090'
    results = match.analyze_text(number, types)
    
    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability > 0.45 and results[0].probability < 0.6

def test_phone_number_medium_match_with_phone_context():
    number = '425 8829090'
    context = 'my phone number is '
    results = match.analyze_text(context + number, types)
    
    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability > 0.75 and results[0].probability < 0.9


def test_phone_number_medium_match_with_irrelevant_context():
    number = '425 8829090'
    context = 'This is just a sentence '
    results = match.analyze_text(context + number, types)
    
    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability > 0.29 and results[0].probability < 0.51


def test_phone_number_weak_match_no_context():
    number = '4258829090'
    results = match.analyze_text(number, types)
    
    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability > 0 and results[0].probability < 0.3


def test_phone_number_weak_match_with_phone_context():
    number = '4258829090'
    context = 'my phone number is '
    results = match.analyze_text(context + number, types)
    
    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability > 0.59 and results[0].probability < 0.81


def test_phone_numbers_lemmatized_context_phones():
    number1 = '052 5552606'
    number2 = '074-7111234'
    results = match.analyze_text('try one of these phones ' + number1 + ' ' + number2, types)
    
    assert len(results) == 2
    assert results[0].text == number1
    assert results[0].probability > 0.75 and results[0].probability < 0.9
    assert results[1].text == number2
    assert results[0].probability > 0.75 and results[0].probability < 0.9