from analyzer import matcher
from analyzer import common_pb2

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.EMAIL_ADDRESS)
types = [fieldType]


def test_valid_email():
    match = matcher.Matcher()
    email = 'my email is info@presidio.site'
    results = match.analyze_text('the email is ' + email, types)
    assert len(results) == 1


def test_invalid_email():
    match = matcher.Matcher()
    email = 'my email is info@presidio.'
    results = match.analyze_text('the email is ' + email, types)
    assert len(results) == 0
