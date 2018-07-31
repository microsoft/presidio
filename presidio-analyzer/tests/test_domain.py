from analyzer import matcher, common_pb2
from tests import *


fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.DOMAIN_NAME)
types = [fieldType]


def test_invalid_domain():
    domain = 'microsoft.'
    results = match.analyze_text(domain, types)

    assert len(results) == 0


def test_invalid_domain_with_exact_context():
    domain = 'microsoft.'
    context = 'my domain is '
    results = match.analyze_text(context + domain, types)

    assert len(results) == 0


def test_valid_domain():
    domain = 'microsoft.com'
    results = match.analyze_text(domain, types)

    assert len(results) == 1
    assert results[0].text == domain
    assert results[0].probability == 1


def test_valid_domains_lemmatized_text():
    domain1 = 'microsoft.com'
    domain2 = '192.168.0.1'
    results = match.analyze_text(
        'my domains: {} {}'.format(
            domain1, domain2), types)

    assert len(results) == 1
