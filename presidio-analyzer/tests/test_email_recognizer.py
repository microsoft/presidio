from analyzer.predefined_recognizers import EmailRecognizer

email_recognizer = EmailRecognizer()
entities = ["EMAIL_ADDRESS"]


def test_valid_email_no_context():
    email = 'info@presidio.site'
    results = email_recognizer.analyze(email, entities)

    assert len(results) == 1
    assert results[0].score == 1.0
    assert results[0].entity_type == entities[0]
    assert results[0].start == 0
    assert results[0].end == 18


def test_valid_email_with_context():
    email = 'info@presidio.site'
    results = email_recognizer.analyze('my email is {}'.format(email), entities)

    assert len(results) == 1
    assert results[0].score == 1.0
    assert results[0].entity_type == entities[0]
    assert results[0].start == 12
    assert results[0].end == 30


def test_multiple_emails_with_lemmatized_context():
    email1 = 'info@presidio.site'
    email2 = 'anotherinfo@presidio.site'
    results = email_recognizer.analyze(
        'try one of this emails: {} or {}'.format(email1, email2), entities)

    assert len(results) == 2
    assert results[0].score == 1.0
    assert results[0].entity_type == entities[0]
    assert results[0].start == 24
    assert results[0].end == 42

    assert results[1].score == 1.0
    assert results[1].entity_type == entities[0]
    assert results[1].start == 46
    assert results[1].end == 71


def test_invalid_email():
    email = 'my email is info@presidio.'
    results = email_recognizer.analyze('the email is ' + email, entities)

    assert len(results) == 0
