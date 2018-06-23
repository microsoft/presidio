from analyzer import matcher, common_pb2
from tests import *


fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.PERSON)
types = [fieldType]


def test_person_first_name():
    name = 'Dan'
    results = match.analyze_text(name, types)

    assert len(results) == 0
    
def test_person_first_name_with_context():
    name = 'Dan'
    context = 'my name is '
    results = match.analyze_text(context + name, types)

    assert len(results) == 1
    assert results[0].text == name
    assert results[0].probability >= matcher.NER_STRENGTH


def test_person_full_name():
    name = 'Dan Tailor'
    results = match.analyze_text(name, types)

    assert len(results) == 1
    assert results[0].text == name
    assert results[0].probability >= matcher.NER_STRENGTH


def test_person_full_name_with_context():
    name = 'John Oliver'
    results = match.analyze_text(name + " is the funniest comedian", types)
    
    assert len(results) == 1
    assert results[0].text == name
    assert results[0].probability >= matcher.NER_STRENGTH


def test_person_last_name():
    name = 'Tailor'
    results = match.analyze_text(name, types)

    assert len(results) == 0


'''
Issue #40 - NER context is limitted
def test_person_last_name_with_context():
    name = 'Tailor'
    context = 'Mr. '
    results = match.analyze_text(context + name, types)

    assert len(results) == 1
    assert results[0].text == name
    assert results[0].probability >= matcher.NER_STRENGTH
'''


def test_person_full_middle_name():
    name = 'Richard Milhous Nixon'
    results = match.analyze_text(name, types)

    assert len(results) == 1
    assert results[0].text == name
    assert results[0].probability >= matcher.NER_STRENGTH


def test_person_full_middle_letter_name():
    name = 'Richard M. Nixon'
    results = match.analyze_text(name, types)

    assert len(results) == 1
    assert results[0].text == name
    assert results[0].probability >= matcher.NER_STRENGTH


def test_person_full_name_complex():
    name = 'Richard (Ric) C. Henderson'
    results = match.analyze_text(name, types)

    assert len(results) == 1
    assert results[0].text == name
    assert results[0].probability >= matcher.NER_STRENGTH

'''
Spacy bug: identifies the name as 3 PERSON entities, instead of one, when adding context
def test_person_full_name_complex_with_context():
    name = 'Richard (Ric) C. Henderson'
    context = 'yesterday I had a meeting with '
    results = match.analyze_text(context + name, types)

    assert len(results) == 1
    assert results[0].text == name
    assert results[0].probability >= matcher.NER_STRENGTH
'''