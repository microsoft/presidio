from analyzer import matcher
from tests import *
import datetime
import os

types = []

def test_all_fields_demo_file():
    start_time = datetime.datetime.now()
    path = os.path.dirname(__file__) + '/data/demo.txt'
    text_file = open(path, 'r')
    text = text_file.read()
    results = match.analyze_text(text, types)
    test_time = datetime.datetime.now() - start_time

    assert len(results) == 20
    assert test_time.seconds < 1
    assert test_time.microseconds < 400000
    print('test_all_fields_demo runtime: {} seconds, {} microseconds'.format(
        test_time.seconds, test_time.microseconds))


def test_all_fields_enron_file():
    start_time = datetime.datetime.now()
    path = os.path.dirname(__file__) + '/data/enron.txt'
    text_file = open(path, 'r')
    text = text_file.read()
    results = match.analyze_text(text, types)
    test_time = datetime.datetime.now() - start_time
    
    assert len(results) > 30
    assert test_time.seconds < 1
    assert test_time.microseconds < 470000
    print('test_all_fields_enron runtime: {} seconds, {} microseconds'.format(
        test_time.seconds, test_time.microseconds))


# Test no duplicates of matches with checksum matches

def test_no_duplicates_of_checkseum_credit_card_no_dashes():
    number = '6011577631711174'
    results = match.analyze_text(number, [])

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0


def test_no_duplicates_of_checkseum_credit_card_with_dashes():
    number = '6011-5776-3171-1174'
    results = match.analyze_text(number, [])

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0


def test_no_duplicates_of_checkseum_crypto():
    wallet = '16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ'
    results = match.analyze_text(wallet, [])

    assert len(results) == 1
    assert results[0].text == wallet
    assert results[0].probability == 1.0


def test_no_duplicates_of_checkseum_domain():
    domain = 'microsoft.com'
    results = match.analyze_text(domain, types)

    assert len(results) == 1
    assert results[0].text == domain
    assert results[0].probability == 1


def test_no_duplicates_of_checkseum_email():
    email = 'my email is info@presidio.site'
    domain = 'presidio.site'
    results = match.analyze_text('the email is ' + email, types)
    results_text = map(lambda r: r.text, results)

    # In email, the domain is also detected with checksum and probability = 1
    assert len(results) == 2

    assert results[0].text in results_text
    assert results[0].probability == 1
    assert results[1].text in results_text
    assert results[0].probability == 1
    assert results[0].text != results[1].text


def test_no_duplicates_of_checkseum_iban():
    number = 'IL150120690000003111111'
    results = match.analyze_text(number, [])

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0
