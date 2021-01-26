import pytest
from common.methods import analyze, analyzer_supported_entities
import json


@pytest.mark.api
def test_given_a_correct_analyze_input_then_return_full_response():
    request_body = {
        "text": "John Smith drivers license is AC432223", "language": "en"}

    response_status, response_content = analyze(request_body)

    assert response_status == 200
    assert response_content == [
        '{\'entity_type\': \'PERSON\', \'start\': 0, \'end\': 10, \'score\': 0.85, \'analysis_explanation\': {\'recognizer\': \'SpacyRecognizer\', \'pattern_name\': None, \'pattern\': None, \'original_score\': 0.85, \'score\': 0.85, \'textual_explanation\': "Identified as PERSON by Spacy\'s Named Entity Recognition", \'score_context_improvement\': 0, \'supportive_context_word\': \'\', \'validation_result\': None}}',
        "{'entity_type': 'US_DRIVER_LICENSE', 'start': 30, 'end': 38, 'score': 0.6499999999999999, 'analysis_explanation': {'recognizer': 'UsLicenseRecognizer', 'pattern_name': 'Driver License - Alphanumeric (weak)', 'pattern': '\\\\b([A-Z][0-9]{3,6}|[A-Z][0-9]{5,9}|[A-Z][0-9]{6,8}|[A-Z][0-9]{4,8}|[A-Z][0-9]{9,11}|[A-Z]{1,2}[0-9]{5,6}|H[0-9]{8}|V[0-9]{6}|X[0-9]{8}|A-Z]{2}[0-9]{2,5}|[A-Z]{2}[0-9]{3,7}|[0-9]{2}[A-Z]{3}[0-9]{5,6}|[A-Z][0-9]{13,14}|[A-Z][0-9]{18}|[A-Z][0-9]{6}R|[A-Z][0-9]{9}|[A-Z][0-9]{1,12}|[0-9]{9}[A-Z]|[A-Z]{2}[0-9]{6}[A-Z]|[0-9]{8}[A-Z]{2}|[0-9]{3}[A-Z]{2}[0-9]{4}|[A-Z][0-9][A-Z][0-9][A-Z]|[0-9]{7,8}[A-Z])\\\\b', 'original_score': 0.3, 'score': 0.6499999999999999, 'textual_explanation': None, 'score_context_improvement': 0.3499999999999999, 'supportive_context_word': 'driver', 'validation_result': None}}"]


@pytest.mark.api
def test_given_a_correct_input_for_supported_entities_then_expect_a_correct_response():
    language_query_parameter = "language=en"
    expected_list = sorted(json.loads(
        '["PHONE_NUMBER", "US_DRIVER_LICENSE", "US_PASSPORT", "SG_NRIC_FIN", "LOCATION", "CREDIT_CARD", "CRYPTO", "UK_NHS", "US_SSN", "US_BANK_NUMBER", "EMAIL_ADDRESS", "DATE_TIME", "IP_ADDRESS", "PERSON", "IBAN_CODE", "NRP", "US_ITIN", "DOMAIN_NAME"]'))

    response_status, response_content = analyzer_supported_entities(language_query_parameter)

    assert response_status == 200
    assert sorted(response_content) == expected_list


@pytest.mark.api
def test_given_a_unsupported_language_for_supported_entities_then_expect_an_error():
    language_query_parameter = "language=he"

    response_status, response_content = analyzer_supported_entities(language_query_parameter)

    assert response_status == 500
    assert response_content == json.loads(
        '{"Error": ["No matching recognizers were found to serve the request."]}')


@pytest.mark.api
def test_given_an_illegal_input_for_supported_entities_then_igonre_and_proceed():
    language_query_parameter = "uknown=input"
    expected_list = sorted(json.loads(
        '["PHONE_NUMBER", "US_DRIVER_LICENSE", "US_PASSPORT", "SG_NRIC_FIN", "LOCATION", "CREDIT_CARD", "CRYPTO", "UK_NHS", "US_SSN", "US_BANK_NUMBER", "EMAIL_ADDRESS", "DATE_TIME", "IP_ADDRESS", "PERSON", "IBAN_CODE", "NRP", "US_ITIN", "DOMAIN_NAME"]'))

    response_status, response_content = analyzer_supported_entities(language_query_parameter)

    assert response_status == 200
    assert sorted(response_content) == expected_list