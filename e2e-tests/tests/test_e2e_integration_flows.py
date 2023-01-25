import json
from pathlib import Path

import pytest
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngineProvider

from common.assertions import equal_json_strings
from common.methods import analyze, anonymize, analyzer_supported_entities
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import EngineResult, OperatorResult


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
        "analysis_explanation": null, "recognition_metadata": {"recognizer_name": "SpacyRecognizer"}
        },
        {"entity_type": "US_DRIVER_LICENSE", "start": 30, "end": 38, "score": 0.6499999999999999, 
        "analysis_explanation": null, "recognition_metadata": {"recognizer_name": "UsLicenseRecognizer"}
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

    expected_response = """{"text": "<PERSON> drivers license is AC43****", "items": [{"operator": "mask", "entity_type": "US_DRIVER_LICENSE", "start": 28, "end": 36, "text": "AC43****"}, {"operator": "replace", "entity_type": "PERSON", "start": 0, "end": 8, "text": "<PERSON>"}]}"""

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
        {"entity_type": "PERSON", "start": 0, "end": 10, "score": 0.85, "analysis_explanation": null, "recognition_metadata": {"recognizer_name": "SpacyRecognizer"}}
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

    expected_response = """{"text": "<PERSON> drivers license is AC432223", "items": [{"operator": "replace", "entity_type": "PERSON", "start": 0, "end": 8, "text": "<PERSON>"}]}"""

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
        {"entity_type": "PERSON", "start": 0, "end": 10, "score": 0.85, "analysis_explanation": null, "recognition_metadata": {"recognizer_name": "SpacyRecognizer"}}
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

    expected_response = """{"text": "<PERSON> drivers license is AC432223", "items": [{"operator": "replace", "entity_type": "PERSON", "start": 0, "end": 8, "text": "<PERSON>"}]}"""

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
        "analysis_explanation": null, "recognition_metadata": {"recognizer_name": "SpacyRecognizer"}
        },
        {"entity_type": "US_DRIVER_LICENSE", "start": 30, "end": 38, "score": 0.6499999999999999, 
        "analysis_explanation": null, "recognition_metadata": {"recognizer_name": "UsLicenseRecognizer"}
        }
    ]
    """

    analyzer_data = analyze_and_assert(analyzer_request, expected_response)

    anonymizer_request = {
        "text": analyzer_request["text"],
        "anonymizers": {"ABC": {"type": "replace", "new_value": "<PERSON>"}},
        "analyzer_results": analyzer_data,
    }

    expected_response = """{"text": "<PERSON> drivers license is <US_DRIVER_LICENSE>", "items": [{"operator": "replace", "entity_type": "US_DRIVER_LICENSE", "start": 28, "end": 47, "text": "<US_DRIVER_LICENSE>"}, {"operator": "replace", "entity_type": "PERSON", "start": 0, "end": 8, "text": "<PERSON>"}]}"""

    anonymize_and_assert(anonymizer_request, expected_response)


@pytest.mark.integration
def test_demo_website_text_returns_correct_anonymized_version():
    # Analyzer request info

    dir_path = Path(__file__).resolve().parent.parent
    with open(Path(dir_path, "resources", "demo.txt"), encoding="utf-8") as f:
        text_into_rows = f.read().split("\n")

    text_into_rows = [txt.strip() for txt in text_into_rows]
    text = " ".join(text_into_rows)
    language = "en"
    score_threshold = 0.35

    analyzer_request = {
        "text": text,
        "language": language,
        "score_threshold": score_threshold,
    }

    # Call analyzer

    analyzer_status_code, analyzer_content = analyze(json.dumps(analyzer_request))

    analyzer_data = json.loads(analyzer_content)

    # Anonymizer request info

    anonymizer_request = {
        "text": analyzer_request["text"],
        "analyzer_results": analyzer_data,
    }

    # Call anonymizer

    anonymizer_status_code, anonymizer_response = anonymize(
        json.dumps(anonymizer_request)
    )

    anonymizer_response_dict = json.loads(anonymizer_response)
    actual_anonymized_text = anonymizer_response_dict["text"]

    # Expected output:

    with open(
        Path(dir_path, "resources", "demo_anonymized.txt"), encoding="utf-8"
    ) as f_exp:
        text_into_rows = f_exp.read().split("\n")

    text_into_rows = [txt.strip() for txt in text_into_rows]
    expected_anonymized_text = " ".join(text_into_rows)

    # Assert equal

    assert expected_anonymized_text == actual_anonymized_text


@pytest.mark.package
def test_given_text_with_pii_using_package_then_analyze_and_anonymize_complete_successfully():
    text_to_test = "John Smith drivers license is AC432223"

    expected_response = [
        RecognizerResult("PERSON", 0, 10, 0.85),
        RecognizerResult("US_DRIVER_LICENSE", 30, 38, 0.6499999999999999),
    ]
    # Create configuration containing engine name and models
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
    }

    # Create NLP engine based on configuration
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()

    # Pass the created NLP engine and supported_languages to the AnalyzerEngine
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
    analyzer_results = analyzer.analyze(text_to_test, "en")
    for i in range(len(analyzer_results)):
        assert analyzer_results[i] == expected_response[i]

    expected_response = EngineResult(
        text="<PERSON> drivers license is <US_DRIVER_LICENSE>"
    )
    expected_response.add_item(
        OperatorResult(
            operator="replace",
            entity_type="US_DRIVER_LICENSE",
            start=28,
            end=47,
            text="<US_DRIVER_LICENSE>",
        )
    )
    expected_response.add_item(
        OperatorResult(
            operator="replace",
            entity_type="PERSON",
            start=0,
            end=8,
            text="<PERSON>",
        )
    )

    anonymizer = AnonymizerEngine()
    anonymizer_results = anonymizer.anonymize(text_to_test, analyzer_results)
    assert anonymizer_results == expected_response
