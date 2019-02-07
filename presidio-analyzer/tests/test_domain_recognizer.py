from analyzer.predefined_recognizers import DomainRecognizer

domain_recognizer = DomainRecognizer()
entities = ["DOMAIN_NAME"]


def test_invalid_domain():
    domain = 'microsoft.'
    results = domain_recognizer.analyze(domain, entities)

    assert len(results) == 0


def test_invalid_domain_with_exact_context():
    domain = 'microsoft.'
    context = 'my domain is '
    results = domain_recognizer.analyze(context + domain, entities)

    assert len(results) == 0


def test_valid_domain():
    domain = 'microsoft.com'
    results = domain_recognizer.analyze(domain, entities)

    assert len(results) == 1
    assert results[0].score == 1
    assert results[0].entity_type == entities[0]
    assert results[0].start == 0
    assert results[0].end == 13


def test_valid_domains_lemmatized_text():
    domain1 = 'microsoft.com'
    domain2 = '192.168.0.1'
    results = domain_recognizer.analyze('my domains: {} {}'.format(domain1, domain2), entities)

    assert len(results) == 2
    assert results[0].entity_type == entities[0]
    assert results[0].start == 12
    assert results[0].end == 25
    assert results[0].score == 1.0

    assert results[1].entity_type == entities[0]
    assert results[1].start == 26
    assert results[1].end == 33
    assert results[1].score == 0

