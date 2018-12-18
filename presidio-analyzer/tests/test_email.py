from analyzer import matcher, common_pb2
from tests import *

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.EMAIL_ADDRESS)
types = [fieldType]


def test_valid_email_no_context():
    email = 'info@presidio.site'
    results = match.analyze_text(email, types)

    assert len(results) == 1
    assert results[0].text == email
    assert results[0].score == 1.0


def test_valid_email_with_context():
    email = 'info@presidio.site'
    results = match.analyze_text('my email is {}'.format(email), types)

    assert len(results) == 1
    assert results[0].text == email
    assert results[0].score == 1.0


def test_multiple_emails_with_lemmatized_context():
    email1 = 'info@presidio.site'
    email2 = 'anotherinfo@presidio.site'
    results = match.analyze_text(
        'try one of thie emails: {} or {}'.format(email1, email2), types)

    assert len(results) == 2
    assert results[0].text == email1
    assert results[0].score == 1.0
    assert results[1].text == email2
    assert results[1].score == 1.0


def test_invalid_email():
    email = 'my email is info@presidio.'
    results = match.analyze_text('the email is ' + email, types)

    assert len(results) == 0
