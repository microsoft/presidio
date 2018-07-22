from analyzer import matcher
from analyzer import common_pb2

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.PHONE_NUMBER)
types = [fieldType]


def test_phone_number_exact_context():
    match = matcher.Matcher()
    number = '052-5552606'
    results = match.analyze_text('my phone number is ' + number, types)
    
    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0

def test_phone_number_similar_context():
    match = matcher.Matcher()
    number = '052-5552606'
    results = match.analyze_text('give me a ring ' + number, types)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability >= matcher.CONTEXT_SIMILARITY_THRESHOLD

def test_phone_numbers_lemmatized_context():
    match = matcher.Matcher()
    number1 = '052-5552606'
    number2 = '074-7111234'
    results = match.analyze_text('try one of these numbers ' + number1 + ' ' + number2, types)
    
    assert len(results) == 2
    assert results[0].text == number1
    assert results[0].probability == 1.0
    assert results[1].text == number2
    assert results[1].probability == 1.0

def test_id_number():
    match = matcher.Matcher()
    number = '0525552606'
    results = match.analyze_text('my id: ' + number, types)
    
    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability <= matcher.CONTEXT_SIMILARITY_THRESHOLD

def test_id_number():
    match = matcher.Matcher()
    number = '0525552606'
    results = match.analyze_text('my id number is: ' + number, types)
    
    '''code should be fixed so that this test will fail. Consider: ignoring 'number' as keyword, since it is too generic'''
    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability <= matcher.CONTEXT_SIMILARITY_THRESHOLD