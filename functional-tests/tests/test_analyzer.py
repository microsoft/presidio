import pytest
from common.methods import analyze


@pytest.mark.api
def test_anonymize():
    request_body = {
        "text": "John Smith drivers license is AC432223", "language": "en"}

    response_status, response_content = analyze(request_body)

    assert response_status == 200
    assert response_content == [
        {"entity_type": "PERSON", "start": 0, "end": 10, "score": 0.85, "analysis_explanation": {"recognizer": "SpacyRecognizer", "pattern_name": None, "pattern": None, "original_score": 0.85,
                                                                                                 "score": 0.85, "textual_explanation": "Identified as PERSON by Spacy\"s Named Entity Recognition", "score_context_improvement": 0, "supportive_context_word": "", "validation_result": None}},
        {"entity_type": "US_DRIVER_LICENSE", "start": 30, "end": 38, "score": 0.6499999999999999, "analysis_explanation": {"recognizer": "UsLicenseRecognizer",
                                                                                                                           "pattern_name": "Driver License - Alphanumeric (weak)", "pattern": "\\\\b([A-Z][0-9]{3,6}|[A-Z][0-9]{5,9}|[A-Z][0-9]{6,8}|[A-Z][0-9]{4,8}|[A-Z][0-9]{9,11}|[A-Z]{1,2}[0-9]{5,6}|H[0-9]{8}|V[0-9]{6}|X[0-9]{8}|A-Z]{2}[0-9]{2,5}|[A-Z]{2}[0-9]{3,7}|[0-9]{2}[A-Z]{3}[0-9]{5,6}|[A-Z][0-9]{13,14}|[A-Z][0-9]{18}|[A-Z][0-9]{6}R|[A-Z][0-9]{9}|[A-Z][0-9]{1,12}|[0-9]{9}[A-Z]|[A-Z]{2}[0-9]{6}[A-Z]|[0-9]{8}[A-Z]{2}|[0-9]{3}[A-Z]{2}[0-9]{4}|[A-Z][0-9][A-Z][0-9][A-Z]|[0-9]{7,8}[A-Z])\\\\b", "original_score": 0.3, "score": 0.6499999999999999, "textual_explanation": None, "score_context_improvement": 0.3499999999999999, "supportive_context_word": "driver", "validation_result": None}}
    ]
