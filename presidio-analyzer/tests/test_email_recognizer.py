from analyzer.predefined_recognizers import EmailRecognizer

email_recognizer = EmailRecognizer()
entities = ["EMAIL_ADDRESS"]


def test_valid_email_no_context():
    email = 'info@presidio.site'
    results = email_recognizer.analyze_all(email, entities)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_valid_email_with_context():
    email = 'info@presidio.site'
    results = email_recognizer.analyze_all('my email is {}'.format(email), entities)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_multiple_emails_with_lemmatized_context():
    email1 = 'info@presidio.site'
    email2 = 'anotherinfo@presidio.site'
    results = email_recognizer.analyze_all(
        'try one of this emails: {} or {}'.format(email1, email2), entities)

    assert len(results) == 2
    assert results[0].score == 1.0
    assert results[1].score == 1.0


def test_invalid_email():
    email = 'my email is info@presidio.'
    results = email_recognizer.analyze_all('the email is ' + email, entities)

    assert len(results) == 0
