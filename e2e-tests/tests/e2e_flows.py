import pytest
import json

from common.assertions import equal_json_strings
from common.methods import analyze, anonymize, analyzer_supported_entities


@pytest.mark.api
def test_given_a_correct_analyze_input_then_anonymize_success():
    analyzer_request = json.loads("""
    {
        "text": "John Smith drivers license is AC432223",
        "language": "en"
    }
    """)

    response_status, response_content = analyze(json.dumps(analyzer_request))

    expected_response = """
    [
        {"entity_type": "PERSON", "start": 0, "end": 10, "score": 0.85, 
        "analysis_explanation": {
            "recognizer": "SpacyRecognizer", "pattern_name": null, "pattern": null, "original_score": 0.85, 
            "score": 0.85, "textual_explanation": "Identified as PERSON by Spacy's Named Entity Recognition", 
            "score_context_improvement": 0, "supportive_context_word": "", "validation_result": null 
            }
        },
        {"entity_type": "US_DRIVER_LICENSE", "start": 30, "end": 38, "score": 0.6499999999999999, 
        "analysis_explanation": {
            "recognizer": "UsLicenseRecognizer", "pattern_name": "Driver License - Alphanumeric (weak)", 
            "pattern": "\\\\b([A-Z][0-9]{3,6}|[A-Z][0-9]{5,9}|[A-Z][0-9]{6,8}|[A-Z][0-9]{4,8}|[A-Z][0-9]{9,11}|[A-Z]{1,2}[0-9]{5,6}|H[0-9]{8}|V[0-9]{6}|X[0-9]{8}|A-Z]{2}[0-9]{2,5}|[A-Z]{2}[0-9]{3,7}|[0-9]{2}[A-Z]{3}[0-9]{5,6}|[A-Z][0-9]{13,14}|[A-Z][0-9]{18}|[A-Z][0-9]{6}R|[A-Z][0-9]{9}|[A-Z][0-9]{1,12}|[0-9]{9}[A-Z]|[A-Z]{2}[0-9]{6}[A-Z]|[0-9]{8}[A-Z]{2}|[0-9]{3}[A-Z]{2}[0-9]{4}|[A-Z][0-9][A-Z][0-9][A-Z]|[0-9]{7,8}[A-Z])\\\\b", 
            "original_score": 0.3, "score": 0.6499999999999999, "textual_explanation": null, 
            "score_context_improvement": 0.3499999999999999, "supportive_context_word": "driver", 
            "validation_result": null 
            }
        }
    ]
    """
    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)

    analyzer_data = json.loads(response_content)

    anonymizer_request = {
        "text": analyzer_request["text"],
        "transformations": {
            "DEFAULT": {"type": "replace", "new_value": "ANONYMIZED"},
            "US_DRIVER_LICENSE": {"type": "mask", "masking_char": "*", "chars_to_mask": 4, "from_end": True},
            "PERSON": {"type": "replace", "new_value": "<PERSON>"}
        },
        "analyzer_results": analyzer_data
    }

    response_status, response_content = anonymize(json.dumps(anonymizer_request))

    expected_response = (
        """{"result":"<PERSON> drivers license is AC43****"}"""
    )
    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_a_correct_analyze_input_high_threashold_then_anonymize_partially():
    analyzer_request = json.loads("""
    {
        "text": "John Smith drivers license is AC432223",
        "language": "en",
        "remove_interpretability_response": 1,
        "score_threshold": 0.7
    }
    """)

    response_status, response_content = analyze(json.dumps(analyzer_request))

    expected_response = """
    [
        {"entity_type": "PERSON", "start": 0, "end": 10, "score": 0.85, "analysis_explanation": null}
    ]
    """
    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)

    analyzer_data = json.loads(response_content)

    anonymizer_request = {
        "text": analyzer_request["text"],
        "transformations": {
            "DEFAULT": {"type": "replace", "new_value": "ANONYMIZED"},
            "US_DRIVER_LICENSE": {"type": "mask", "masking_char": "*", "chars_to_mask": 4, "from_end": True},
            "PERSON": {"type": "replace", "new_value": "<PERSON>"}
        },
        "analyzer_results": analyzer_data
    }

    response_status, response_content = anonymize(json.dumps(anonymizer_request))

    expected_response = (
        """{"result":"<PERSON> drivers license is AC432223"}"""
    )
    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_a_correct_analyze_input_high_threashold_and_upported_entities_then_anonymize_partially():
    language_query_parameter = "language=en"

    response_status, response_content = analyzer_supported_entities(
        language_query_parameter
    )

    assert response_status == 200
    suppotred_entities = json.loads(response_content)

    analyzer_request = {
        "text": "John Smith drivers license is AC432223",
        "language": "en",
        "remove_interpretability_response": 1,
        "score_threshold": 0.7,
        "entities": suppotred_entities
    }

    response_status, response_content = analyze(json.dumps(analyzer_request))

    expected_response = """
    [
        {"entity_type": "PERSON", "start": 0, "end": 10, "score": 0.85, "analysis_explanation": null}
    ]
    """
    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)

    analyzer_data = json.loads(response_content)

    anonymizer_request = {
        "text": analyzer_request["text"],
        "transformations": {
            "DEFAULT": {"type": "replace", "new_value": "ANONYMIZED"},
            "US_DRIVER_LICENSE": {"type": "mask", "masking_char": "*", "chars_to_mask": 4, "from_end": True},
            "PERSON": {"type": "replace", "new_value": "<PERSON>"}
        },
        "analyzer_results": analyzer_data
    }

    response_status, response_content = anonymize(json.dumps(anonymizer_request))

    expected_response = (
        """{"result":"<PERSON> drivers license is AC432223"}"""
    )
    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_an_unknown_entity_then_anonymize_uses_defaults():
    analyzer_request = json.loads("""
    {
        "text": "John Smith drivers license is AC432223",
        "language": "en"
    }
    """)

    response_status, response_content = analyze(json.dumps(analyzer_request))

    expected_response = """
    [
        {"entity_type": "PERSON", "start": 0, "end": 10, "score": 0.85, 
        "analysis_explanation": {
            "recognizer": "SpacyRecognizer", "pattern_name": null, "pattern": null, "original_score": 0.85, 
            "score": 0.85, "textual_explanation": "Identified as PERSON by Spacy's Named Entity Recognition", 
            "score_context_improvement": 0, "supportive_context_word": "", "validation_result": null 
            }
        },
        {"entity_type": "US_DRIVER_LICENSE", "start": 30, "end": 38, "score": 0.6499999999999999, 
        "analysis_explanation": {
            "recognizer": "UsLicenseRecognizer", "pattern_name": "Driver License - Alphanumeric (weak)", 
            "pattern": "\\\\b([A-Z][0-9]{3,6}|[A-Z][0-9]{5,9}|[A-Z][0-9]{6,8}|[A-Z][0-9]{4,8}|[A-Z][0-9]{9,11}|[A-Z]{1,2}[0-9]{5,6}|H[0-9]{8}|V[0-9]{6}|X[0-9]{8}|A-Z]{2}[0-9]{2,5}|[A-Z]{2}[0-9]{3,7}|[0-9]{2}[A-Z]{3}[0-9]{5,6}|[A-Z][0-9]{13,14}|[A-Z][0-9]{18}|[A-Z][0-9]{6}R|[A-Z][0-9]{9}|[A-Z][0-9]{1,12}|[0-9]{9}[A-Z]|[A-Z]{2}[0-9]{6}[A-Z]|[0-9]{8}[A-Z]{2}|[0-9]{3}[A-Z]{2}[0-9]{4}|[A-Z][0-9][A-Z][0-9][A-Z]|[0-9]{7,8}[A-Z])\\\\b", 
            "original_score": 0.3, "score": 0.6499999999999999, "textual_explanation": null, 
            "score_context_improvement": 0.3499999999999999, "supportive_context_word": "driver", 
            "validation_result": null 
            }
        }
    ]
    """
    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)

    analyzer_data = json.loads(response_content)

    anonymizer_request = {
        "text": analyzer_request["text"],
        "transformations": {
            "ABC": {"type": "replace", "new_value": "<PERSON>"}
        },
        "analyzer_results": analyzer_data
    }

    response_status, response_content = anonymize(json.dumps(anonymizer_request))

    expected_response = (
        """{"result":"<PERSON> drivers license is <US_DRIVER_LICENSE>"}"""
    )
    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_an_unknown_anonymizer_then_anonymize_fails():
    analyzer_request = json.loads("""
    {
        "text": "John Smith drivers license is AC432223",
        "language": "en"
    }
    """)

    response_status, response_content = analyze(json.dumps(analyzer_request))

    expected_response = """
    [
        {"entity_type": "PERSON", "start": 0, "end": 10, "score": 0.85, 
        "analysis_explanation": {
            "recognizer": "SpacyRecognizer", "pattern_name": null, "pattern": null, "original_score": 0.85, 
            "score": 0.85, "textual_explanation": "Identified as PERSON by Spacy's Named Entity Recognition", 
            "score_context_improvement": 0, "supportive_context_word": "", "validation_result": null 
            }
        },
        {"entity_type": "US_DRIVER_LICENSE", "start": 30, "end": 38, "score": 0.6499999999999999, 
        "analysis_explanation": {
            "recognizer": "UsLicenseRecognizer", "pattern_name": "Driver License - Alphanumeric (weak)", 
            "pattern": "\\\\b([A-Z][0-9]{3,6}|[A-Z][0-9]{5,9}|[A-Z][0-9]{6,8}|[A-Z][0-9]{4,8}|[A-Z][0-9]{9,11}|[A-Z]{1,2}[0-9]{5,6}|H[0-9]{8}|V[0-9]{6}|X[0-9]{8}|A-Z]{2}[0-9]{2,5}|[A-Z]{2}[0-9]{3,7}|[0-9]{2}[A-Z]{3}[0-9]{5,6}|[A-Z][0-9]{13,14}|[A-Z][0-9]{18}|[A-Z][0-9]{6}R|[A-Z][0-9]{9}|[A-Z][0-9]{1,12}|[0-9]{9}[A-Z]|[A-Z]{2}[0-9]{6}[A-Z]|[0-9]{8}[A-Z]{2}|[0-9]{3}[A-Z]{2}[0-9]{4}|[A-Z][0-9][A-Z][0-9][A-Z]|[0-9]{7,8}[A-Z])\\\\b", 
            "original_score": 0.3, "score": 0.6499999999999999, "textual_explanation": null, 
            "score_context_improvement": 0.3499999999999999, "supportive_context_word": "driver", 
            "validation_result": null 
            }
        }
    ]
    """
    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)

    analyzer_data = json.loads(response_content)

    anonymizer_request = {
        "text": analyzer_request["text"],
        "transformations": {
            "PERSON": {"type": "abc", "new_value": "xyz"}
        },
        "analyzer_results": analyzer_data
    }

    response_status, response_content = anonymize(json.dumps(anonymizer_request))

    expected_response = (
        """{"error": "Invalid anonymizer class \'abc\'."}"""
    )
    assert response_status == 422
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_no_text_to_anonymizer_then_anonymize_fails():
    analyzer_request = json.loads("""
    {
        "text": "John Smith drivers license is AC432223",
        "language": "en"
    }
    """)

    response_status, response_content = analyze(json.dumps(analyzer_request))

    expected_response = """
    [
        {"entity_type": "PERSON", "start": 0, "end": 10, "score": 0.85, 
        "analysis_explanation": {
            "recognizer": "SpacyRecognizer", "pattern_name": null, "pattern": null, "original_score": 0.85, 
            "score": 0.85, "textual_explanation": "Identified as PERSON by Spacy's Named Entity Recognition", 
            "score_context_improvement": 0, "supportive_context_word": "", "validation_result": null 
            }
        },
        {"entity_type": "US_DRIVER_LICENSE", "start": 30, "end": 38, "score": 0.6499999999999999, 
        "analysis_explanation": {
            "recognizer": "UsLicenseRecognizer", "pattern_name": "Driver License - Alphanumeric (weak)", 
            "pattern": "\\\\b([A-Z][0-9]{3,6}|[A-Z][0-9]{5,9}|[A-Z][0-9]{6,8}|[A-Z][0-9]{4,8}|[A-Z][0-9]{9,11}|[A-Z]{1,2}[0-9]{5,6}|H[0-9]{8}|V[0-9]{6}|X[0-9]{8}|A-Z]{2}[0-9]{2,5}|[A-Z]{2}[0-9]{3,7}|[0-9]{2}[A-Z]{3}[0-9]{5,6}|[A-Z][0-9]{13,14}|[A-Z][0-9]{18}|[A-Z][0-9]{6}R|[A-Z][0-9]{9}|[A-Z][0-9]{1,12}|[0-9]{9}[A-Z]|[A-Z]{2}[0-9]{6}[A-Z]|[0-9]{8}[A-Z]{2}|[0-9]{3}[A-Z]{2}[0-9]{4}|[A-Z][0-9][A-Z][0-9][A-Z]|[0-9]{7,8}[A-Z])\\\\b", 
            "original_score": 0.3, "score": 0.6499999999999999, "textual_explanation": null, 
            "score_context_improvement": 0.3499999999999999, "supportive_context_word": "driver", 
            "validation_result": null 
            }
        }
    ]
    """
    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)

    analyzer_data = json.loads(response_content)

    anonymizer_request = {
        "transformations": {
            "PERSON": {"type": "replace", "new_value": "xyz"}
        },
        "analyzer_results": analyzer_data
    }

    response_status, response_content = anonymize(json.dumps(anonymizer_request))

    expected_response = (
        """{"error": "Invalid input, text can not be empty"}"""
    )
    assert response_status == 422
    assert equal_json_strings(expected_response, response_content)