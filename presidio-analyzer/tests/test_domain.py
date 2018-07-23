from analyzer import matcher
from analyzer import common_pb2

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.DOMAIN_NAME)
types = [fieldType]

match = matcher.Matcher()

def test_valid_domain():
    domain = 'microsoft.com 192.168.0.1'
    results = match.analyze_text('the domain is ' + domain, types)
    assert len(results) == 1


def test_invalid_domain():
    domain = 'microsoft.'
    results = match.analyze_text('the domain is ' + domain, types)
    assert len(results) == 0
