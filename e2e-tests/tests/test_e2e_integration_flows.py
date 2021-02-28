import pytest
import json

from common.assertions import equal_json_strings
from common.methods import analyze, anonymize, analyzer_supported_entities


def analyze_and_assert(analyzer_request, expected_response):
    response_status, response_content = analyze(json.dumps(analyzer_request))
    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)
    analyzer_data = json.loads(response_content)
    return analyzer_data


def anonymize_and_assert(anonymizer_request, expected_response):
    response_status, response_content = anonymize(json.dumps(anonymizer_request))
    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.integration
def test_given_text_with_pii_then_analyze_and_anonymize_successfully():
    analyzer_request = {
        "text": "John Smith drivers license is AC432223",
        "language": "en",
    }

    expected_response = """
    [
        {"entity_type": "PERSON", "start": 0, "end": 10, "score": 0.85, 
        "analysis_explanation": null
        },
        {"entity_type": "US_DRIVER_LICENSE", "start": 30, "end": 38, "score": 0.6499999999999999, 
        "analysis_explanation": null
        }
    ]
    """

    analyzer_data = analyze_and_assert(analyzer_request, expected_response)

    anonymizer_request = {
        "text": analyzer_request["text"],
        "anonymizers": {
            "DEFAULT": {"type": "replace", "new_value": "ANONYMIZED"},
            "US_DRIVER_LICENSE": {
                "type": "mask",
                "masking_char": "*",
                "chars_to_mask": 4,
                "from_end": True,
            },
            "PERSON": {"type": "replace", "new_value": "<PERSON>"},
        },
        "analyzer_results": analyzer_data,
    }

    expected_response = """{"result":"<PERSON> drivers license is AC43****"}"""

    anonymize_and_assert(anonymizer_request, expected_response)


@pytest.mark.integration
def test_given_a_correct_analyze_input_high_threashold_then_anonymize_partially():
    analyzer_request = json.loads(
        """
    {
        "text": "John Smith drivers license is AC432223",
        "language": "en",
        "score_threshold": 0.7
    }
    """
    )

    expected_response = """
    [
        {"entity_type": "PERSON", "start": 0, "end": 10, "score": 0.85, "analysis_explanation": null}
    ]
    """

    analyzer_data = analyze_and_assert(analyzer_request, expected_response)

    anonymizer_request = {
        "text": analyzer_request["text"],
        "anonymizers": {
            "DEFAULT": {"type": "replace", "new_value": "ANONYMIZED"},
            "US_DRIVER_LICENSE": {
                "type": "mask",
                "masking_char": "*",
                "chars_to_mask": 4,
                "from_end": True,
            },
            "PERSON": {"type": "replace", "new_value": "<PERSON>"},
        },
        "analyzer_results": analyzer_data,
    }

    expected_response = """{"result":"<PERSON> drivers license is AC432223"}"""

    anonymize_and_assert(anonymizer_request, expected_response)


@pytest.mark.integration
def test_given_a_correct_analyze_input_with_high_threshold_and_unmatched_entities_then_anonymize_partially():
    language_query_parameter = "language=en"

    response_status, response_content = analyzer_supported_entities(
        language_query_parameter
    )

    assert response_status == 200
    suppotred_entities = json.loads(response_content)

    analyzer_request = {
        "text": "John Smith drivers license is AC432223",
        "language": "en",
        "score_threshold": 0.7,
        "entities": suppotred_entities,
    }

    expected_response = """
    [
        {"entity_type": "PERSON", "start": 0, "end": 10, "score": 0.85, "analysis_explanation": null}
    ]
    """

    analyzer_data = analyze_and_assert(analyzer_request, expected_response)

    anonymizer_request = {
        "text": analyzer_request["text"],
        "anonymizers": {
            "DEFAULT": {"type": "replace", "new_value": "ANONYMIZED"},
            "US_DRIVER_LICENSE": {
                "type": "mask",
                "masking_char": "*",
                "chars_to_mask": 4,
                "from_end": True,
            },
            "PERSON": {"type": "replace", "new_value": "<PERSON>"},
        },
        "analyzer_results": analyzer_data,
    }

    expected_response = """{"result":"<PERSON> drivers license is AC432223"}"""

    anonymize_and_assert(anonymizer_request, expected_response)


@pytest.mark.integration
def test_given_an_unknown_entity_then_anonymize_uses_defaults():
    analyzer_request = json.loads(
        """
    {
        "text": "John Smith drivers license is AC432223",
        "language": "en"
    }
    """
    )

    expected_response = """
    [
        {"entity_type": "PERSON", "start": 0, "end": 10, "score": 0.85, 
        "analysis_explanation": null
        },
        {"entity_type": "US_DRIVER_LICENSE", "start": 30, "end": 38, "score": 0.6499999999999999, 
        "analysis_explanation": null
        }
    ]
    """

    analyzer_data = analyze_and_assert(analyzer_request, expected_response)

    anonymizer_request = {
        "text": analyzer_request["text"],
        "anonymizers": {"ABC": {"type": "replace", "new_value": "<PERSON>"}},
        "analyzer_results": analyzer_data,
    }

    expected_response = (
        """{"result":"<PERSON> drivers license is <US_DRIVER_LICENSE>"}"""
    )

    anonymize_and_assert(anonymizer_request, expected_response)
