from analyzer import matcher
from analyzer import common_pb2


fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.PERSON)
types = [fieldType]

match = matcher.Matcher()

def test_person_name_simple():
    name = 'John Oliver'
    results = match.analyze_text(name + " is the funniest comedian", types)
    assert results[0].text == name
