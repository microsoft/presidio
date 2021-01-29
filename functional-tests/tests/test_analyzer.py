import pytest
from common.methods import analyze, analyzer_supported_entities


@pytest.mark.api
def test_given_a_correct_analyze_input_then_return_full_response():
    request_body = {
        "text": "John Smith drivers license is AC432223", "language": "en"}

    response_status, response_content = analyze(request_body)

    assert response_status == 200
    assert response_content == ["{'entity_type': 'PERSON', 'start': 0, 'end': 10, 'score': 0.85, 'analysis_explanation': {'recognizer': 'SpacyRecognizer', 'pattern_name': None, 'pattern': None, 'original_score': 0.85, 'score': 0.85, 'textual_explanation': \"Identified as PERSON by Spacy's Named Entity Recognition\", 'score_context_improvement': 0, 'supportive_context_word': '', 'validation_result': None}}",
    "{'entity_type': 'US_DRIVER_LICENSE', 'start': 30, 'end': 38, 'score': 0.6499999999999999, 'analysis_explanation': {'recognizer': 'UsLicenseRecognizer', 'pattern_name': 'Driver License - Alphanumeric (weak)', 'pattern': '\\\\b([A-Z][0-9]{3,6}|[A-Z][0-9]{5,9}|[A-Z][0-9]{6,8}|[A-Z][0-9]{4,8}|[A-Z][0-9]{9,11}|[A-Z]{1,2}[0-9]{5,6}|H[0-9]{8}|V[0-9]{6}|X[0-9]{8}|A-Z]{2}[0-9]{2,5}|[A-Z]{2}[0-9]{3,7}|[0-9]{2}[A-Z]{3}[0-9]{5,6}|[A-Z][0-9]{13,14}|[A-Z][0-9]{18}|[A-Z][0-9]{6}R|[A-Z][0-9]{9}|[A-Z][0-9]{1,12}|[0-9]{9}[A-Z]|[A-Z]{2}[0-9]{6}[A-Z]|[0-9]{8}[A-Z]{2}|[0-9]{3}[A-Z]{2}[0-9]{4}|[A-Z][0-9][A-Z][0-9][A-Z]|[0-9]{7,8}[A-Z])\\\\b', 'original_score': 0.3, 'score': 0.6499999999999999, 'textual_explanation': None, 'score_context_improvement': 0.3499999999999999, 'supportive_context_word': 'driver', 'validation_result': None}}"]


@pytest.mark.api
def test_given_analyze_threshold_input_then_return_result_above_threshold():
    request_body = {
        "text": "John Smith drivers license is AC432223", "language": "en", "score_threshold": 0.7}

    response_status, response_content = analyze(request_body)

    assert response_status == 200
    assert response_content == ["{'entity_type': 'PERSON', 'start': 0, 'end': 10, 'score': 0.85, 'analysis_explanation': {'recognizer': 'SpacyRecognizer', 'pattern_name': None, 'pattern': None, 'original_score': 0.85, 'score': 0.85, 'textual_explanation': \"Identified as PERSON by Spacy's Named Entity Recognition\", 'score_context_improvement': 0, 'supportive_context_word': '', 'validation_result': None}}"]


@pytest.mark.api
def test_given_no_analyze_text_input_then_return_error():
    request_body = {}

    response_status, response_content = analyze(request_body)

    assert response_status == 500
    assert response_content == {"error": "No text provided"}


@pytest.mark.api
def test_given_no_analyze_language_input_then_return_error():
    request_body = {"language": "en"}

    response_status, response_content = analyze(request_body)

    assert response_status == 500
    assert response_content == {"error": "No text provided"}


@pytest.mark.api
def test_given_analyze_text_no_language_input_then_return_error():
    request_body = {
        "text": "John Smith drivers license is AC432223"}

    response_status, response_content = analyze(request_body)

    assert response_status == 500
    assert response_content == {"error": "No language provided"}


@pytest.mark.api
def test_given_a_incorrect_analyze_language_input_then_return_error():
    request_body = {
        "text": "John Smith drivers license is AC432223", "language": "zz"}

    response_status, response_content = analyze(request_body)

    assert response_status == 500
    assert response_content == {"error": "No matching recognizers were found to serve the request."}


@pytest.mark.api
def test_given_a_correlationid_analyze_input_then_return_normal_response():
    request_body = {
        "text": "John Smith drivers license is AC432223", "language": "en", "correlation_id": "123"}

    response_status, response_content = analyze(request_body)

    assert response_status == 200


@pytest.mark.api
def test_given_a_trace_true_analyze_input_then_return_normal_response():
    request_body = {
        "text": "John Smith drivers license is AC432223", "language": "en", "trace": "1"}

    response_status, response_content = analyze(request_body)

    assert response_status == 200


@pytest.mark.api
def test_given_a_trace_invalid_value_analyze_input_then_return_normal_response():
    request_body = {
        "text": "John Smith drivers license is AC432223", "language": "en", "trace": "somedata"}

    response_status, response_content = analyze(request_body)

    assert response_status == 200


@pytest.mark.api
def test_given_no_interpretability_for_analyze_input_then_return_response_without_anlysis():
    request_body = {
        "text": "John Smith drivers license is AC432223", "language": "en", "remove_interpretability_response": 1}

    response_status, response_content = analyze(request_body)

    assert response_status == 200
    assert response_content == [
                                    "{'entity_type': 'PERSON', 'start': 0, 'end': 10, 'score': 0.85, 'analysis_explanation': None}",
                                    "{'entity_type': 'US_DRIVER_LICENSE', 'start': 30, 'end': 38, 'score': 0.6499999999999999, 'analysis_explanation': None}"
                                ]

@pytest.mark.api
def test_given_interpretability_enabled_for_analyze_input_then_return_response_with_anlysis():
    request_body = {
        "text": "John Smith drivers license is AC432223", "language": "en", "remove_interpretability_response": 0}

    response_status, response_content = analyze(request_body)

    assert response_status == 200
    assert response_content == ["{'entity_type': 'PERSON', 'start': 0, 'end': 10, 'score': 0.85, 'analysis_explanation': {'recognizer': 'SpacyRecognizer', 'pattern_name': None, 'pattern': None, 'original_score': 0.85, 'score': 0.85, 'textual_explanation': \"Identified as PERSON by Spacy's Named Entity Recognition\", 'score_context_improvement': 0, 'supportive_context_word': '', 'validation_result': None}}",
    "{'entity_type': 'US_DRIVER_LICENSE', 'start': 30, 'end': 38, 'score': 0.6499999999999999, 'analysis_explanation': {'recognizer': 'UsLicenseRecognizer', 'pattern_name': 'Driver License - Alphanumeric (weak)', 'pattern': '\\\\b([A-Z][0-9]{3,6}|[A-Z][0-9]{5,9}|[A-Z][0-9]{6,8}|[A-Z][0-9]{4,8}|[A-Z][0-9]{9,11}|[A-Z]{1,2}[0-9]{5,6}|H[0-9]{8}|V[0-9]{6}|X[0-9]{8}|A-Z]{2}[0-9]{2,5}|[A-Z]{2}[0-9]{3,7}|[0-9]{2}[A-Z]{3}[0-9]{5,6}|[A-Z][0-9]{13,14}|[A-Z][0-9]{18}|[A-Z][0-9]{6}R|[A-Z][0-9]{9}|[A-Z][0-9]{1,12}|[0-9]{9}[A-Z]|[A-Z]{2}[0-9]{6}[A-Z]|[0-9]{8}[A-Z]{2}|[0-9]{3}[A-Z]{2}[0-9]{4}|[A-Z][0-9][A-Z][0-9][A-Z]|[0-9]{7,8}[A-Z])\\\\b', 'original_score': 0.3, 'score': 0.6499999999999999, 'textual_explanation': None, 'score_context_improvement': 0.3499999999999999, 'supportive_context_word': 'driver', 'validation_result': None}}"]


def test_given_analyze_entities_input_then_return_results_only_with_those_entities():
    request_body = {
        "text": "John Smith drivers license is AC432223", "language": "en", "entities": ["PERSON"]}

    response_status, response_content = analyze(request_body)

    assert response_status == 200
    assert response_content == ["{'entity_type': 'PERSON', 'start': 0, 'end': 10, 'score': 0.85, 'analysis_explanation': {'recognizer': 'SpacyRecognizer', 'pattern_name': None, 'pattern': None, 'original_score': 0.85, 'score': 0.85, 'textual_explanation': \"Identified as PERSON by Spacy's Named Entity Recognition\", 'score_context_improvement': 0, 'supportive_context_word': '', 'validation_result': None}}"]


@pytest.mark.api
def test_given_a_correct_input_for_supported_entities_then_expect_a_correct_response():
    language_query_parameter = "language=en"
    expected_list = sorted(["PHONE_NUMBER", "US_DRIVER_LICENSE", "US_PASSPORT", "SG_NRIC_FIN", "LOCATION", "CREDIT_CARD", "CRYPTO", "UK_NHS", "US_SSN", "US_BANK_NUMBER", "EMAIL_ADDRESS", "DATE_TIME", "IP_ADDRESS", "PERSON", "IBAN_CODE", "NRP", "US_ITIN", "DOMAIN_NAME"])

    response_status, response_content = analyzer_supported_entities(language_query_parameter)

    assert response_status == 200
    assert sorted(response_content) == expected_list


@pytest.mark.api
def test_given_a_unsupported_language_for_supported_entities_then_expect_an_error():
    language_query_parameter = "language=he"

    response_status, response_content = analyzer_supported_entities(language_query_parameter)

    assert response_status == 500
    assert response_content == {"error": "No matching recognizers were found to serve the request."}


@pytest.mark.api
def test_given_an_illegal_input_for_supported_entities_then_igonre_and_proceed():
    language_query_parameter = "uknown=input"
    expected_list = sorted(["PHONE_NUMBER", "US_DRIVER_LICENSE", "US_PASSPORT", "SG_NRIC_FIN", "LOCATION", "CREDIT_CARD", "CRYPTO", "UK_NHS", "US_SSN", "US_BANK_NUMBER", "EMAIL_ADDRESS", "DATE_TIME", "IP_ADDRESS", "PERSON", "IBAN_CODE", "NRP", "US_ITIN", "DOMAIN_NAME"])

    response_status, response_content = analyzer_supported_entities(language_query_parameter)

    assert response_status == 200
    assert sorted(response_content) == expected_list