"""Tests for the AHDS De-identification service Surrogate operator."""

import os
import importlib
from unittest.mock import MagicMock

import pytest
import dotenv

from presidio_anonymizer.operators import AHDSSurrogate
from presidio_anonymizer.entities import InvalidParamError

@pytest.fixture(scope="module")
def import_modules():
    pytest.importorskip("azure.identity")
    pytest.importorskip("azure.health.deidentification")
    from azure.health.deidentification import DeidentificationClient
    from azure.health.deidentification.models import (
        DeidentificationContent,
        DeidentificationOperationType,
        DeidentificationResult,
        SimplePhiEntity,
        TaggedPhiEntities,
        PhiCategory,
        TextEncodingType,
        DeidentificationCustomizationOptions,
    )
    from azure.identity import DefaultAzureCredential

def requires_env_vars():
    dotenv.load_dotenv()
    endpoint = os.getenv("AHDS_ENDPOINT", "")
    return pytest.mark.skipif(
        endpoint == "",
        reason="AHDS_ENDPOINT environment variable not set"
    )
def test_operator_name(import_modules):
    operator = AHDSSurrogate()
    assert operator.operator_name() == "surrogate_ahds"

@requires_env_vars()
def test_surrogate_only_operation_sample_pattern(import_modules):
    from azure.health.deidentification import DeidentificationClient
    from azure.health.deidentification.models import (
        DeidentificationContent,
        DeidentificationCustomizationOptions,
        DeidentificationOperationType,
        DeidentificationResult,
        PhiCategory,
        SimplePhiEntity,
        TaggedPhiEntities,
        TextEncodingType,
    )
    from azure.identity import DefaultAzureCredential

    endpoint = os.environ["AHDS_ENDPOINT"]
    credential = DefaultAzureCredential()
    client = DeidentificationClient(endpoint, credential)

    tagged_entities = TaggedPhiEntities(
        encoding=TextEncodingType.CODE_POINT,
        entities=[SimplePhiEntity(category=PhiCategory.PATIENT, offset=18, length=10)],
    )

    body = DeidentificationContent(
        input_text="Hello, my name is John Smith.",
        operation_type=DeidentificationOperationType.SURROGATE_ONLY,
        tagged_entities=tagged_entities,
        customizations=DeidentificationCustomizationOptions(input_locale="en-US"),
    )

    try:
        result: DeidentificationResult = client.deidentify_text(body)
        assert result is not None
        assert result.output_text is not None
        assert len(result.output_text) > 0
        assert result.output_text != body.input_text
        print(f'Original Text:        "{body.input_text}"')
        print(f'Surrogate Only Text:  "{result.output_text}"')
    except Exception as e:
        if "DefaultAzureCredential" in str(e) or "authentication" in str(e).lower():
            pytest.skip("Azure authentication not available in test environment")
        elif "Forbidden" in str(e):
            pytest.skip("Azure credentials lack permission to access AHDS service")
        elif "500" in str(e) or "InternalServerError" in str(e):
            pytest.skip("AHDS service temporarily unavailable")
        elif "ApiVersionUnsupported" in str(e):
            pytest.skip("API version not supported by AHDS service")
        else:
            raise

@requires_env_vars()
def test_multiple_entities_surrogate_only(import_modules):
    from azure.health.deidentification import DeidentificationClient
    from azure.health.deidentification.models import (
        DeidentificationContent,
        DeidentificationCustomizationOptions,
        DeidentificationOperationType,
        DeidentificationResult,
        PhiCategory,
        SimplePhiEntity,
        TaggedPhiEntities,
        TextEncodingType,
    )
    from azure.identity import DefaultAzureCredential

    endpoint = os.environ["AHDS_ENDPOINT"]
    credential = DefaultAzureCredential()
    client = DeidentificationClient(endpoint, credential)

    text = "Patient John Doe was seen by Dr. Smith on 2024-01-15. Contact: john.doe@email.com or 555-123-4567."
    tagged_entities = TaggedPhiEntities(
        encoding=TextEncodingType.CODE_POINT,
        entities=[
            SimplePhiEntity(category=PhiCategory.PATIENT, offset=8, length=8),
            SimplePhiEntity(category=PhiCategory.DOCTOR, offset=29, length=9),
            SimplePhiEntity(category=PhiCategory.DATE, offset=42, length=10),
            SimplePhiEntity(category=PhiCategory.EMAIL, offset=63, length=17),
            SimplePhiEntity(category=PhiCategory.PHONE, offset=84, length=12),
        ],
    )

    body = DeidentificationContent(
        input_text=text,
        operation_type=DeidentificationOperationType.SURROGATE_ONLY,
        tagged_entities=tagged_entities,
        customizations=DeidentificationCustomizationOptions(input_locale="en-US"),
    )

    try:
        result: DeidentificationResult = client.deidentify_text(body)
        assert result is not None
        assert result.output_text is not None
        assert result.output_text != text
        print(f'Original Text: "{text}"')
        print(f'Surrogate Text: "{result.output_text}"')
    except Exception as e:
        if "DefaultAzureCredential" in str(e) or "authentication" in str(e).lower():
            pytest.skip("Azure authentication not available in test environment")
        elif "Forbidden" in str(e):
            pytest.skip("Azure credentials lack permission to access AHDS service")
        elif "500" in str(e) or "InternalServerError" in str(e):
            pytest.skip("AHDS service temporarily unavailable")
        else:
            raise

def test_operation_type_is_surrogate_only(import_modules):
    from azure.health.deidentification.models import DeidentificationOperationType
    assert hasattr(DeidentificationOperationType, 'SURROGATE_ONLY')
    assert DeidentificationOperationType.SURROGATE_ONLY == "SurrogateOnly"

def test_phi_categories_available(import_modules):
    from azure.health.deidentification.models import PhiCategory
    required_categories = ['PATIENT', 'DOCTOR', 'DATE', 'PHONE', 'EMAIL']
    for category_name in required_categories:
        assert hasattr(PhiCategory, category_name), f"PhiCategory.{category_name} not available"

@requires_env_vars()
def test_operator_integration_with_ahds_client(import_modules):
    operator = AHDSSurrogate()
    text = "Hello, my name is John Smith."
    entities = [
        {
            'entity_type': 'PERSON',
            'start': 18,
            'end': 28,
            'text': 'John Smith',
            'score': 0.9
        }
    ]
    params = {
        "entities": entities,
        "input_locale": "en-US"
    }
    try:
        result = operator.operate(text, params)
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        assert result != text 
        print(f"Operator Test - Original: {text}")
        print(f"Operator Test - Surrogate: {result}")
    except Exception as e:
        if "DefaultAzureCredential" in str(e) or "authentication" in str(e).lower():
            pytest.skip("Azure authentication not available in test environment")
        elif "Forbidden" in str(e):
            pytest.skip("Azure credentials lack permission to access AHDS service")
        elif "500" in str(e) or "InternalServerError" in str(e):
            pytest.skip("AHDS service temporarily unavailable")
        else:
            raise

@requires_env_vars()
def test_integration_with_real_service(import_modules):
    operator = AHDSSurrogate()
    text = "Patient John Doe was seen by Dr. Smith on 2024-01-15"
    mock_entities = [
        {
            'entity_type': 'PERSON', 
            'start': 8, 
            'end': 16, 
            'text': 'John Doe',
            'score': 0.9
        },
        {
            'entity_type': 'DOCTOR', 
            'start': 29, 
            'end': 38, 
            'text': 'Dr. Smith',
            'score': 0.9
        },
        {
            'entity_type': 'DATE_TIME', 
            'start': 42, 
            'end': 52, 
            'text': '2024-01-15',
            'score': 0.9
        }
    ]
    params = {
        "entities": mock_entities,
        "input_locale": "en-US"
    }
    try:
        result = operator.operate(text, params)
        assert result is not None
        assert len(result) > 0
        assert result != text
        length_diff = abs(len(result) - len(text))
        assert length_diff < 50, f"Result length too different: {len(result)} vs {len(text)}"
        print(f"Original: {text}")
        print(f"Surrogate: {result}")
    except Exception as e:
        if "Forbidden" in str(e):
            pytest.skip("Azure credentials lack permission to access AHDS service")
        elif "500" in str(e) or "InternalServerError" in str(e):
            pytest.skip("AHDS service temporarily unavailable")
        else:
            raise

def test_entity_mapping_to_phi_categories(import_modules):
    operator = AHDSSurrogate()
    test_cases = [
        ("PATIENT", "PATIENT"),
        ("PERSON", "PATIENT"), 
        ("DOCTOR", "DOCTOR"),
        ("DATE", "DATE"),
        ("PHONE_NUMBER", "PHONE"),
        ("EMAIL_ADDRESS", "EMAIL"),
        ("US_SSN", "SOCIAL_SECURITY"),
        ("UNKNOWN_TYPE", "UNKNOWN")
    ]
    from azure.health.deidentification.models import PhiCategory
    for entity_type, expected_category in test_cases:
        phi_category = operator._map_to_phi_category(entity_type)
        assert phi_category is not None
        expected_phi_category = getattr(PhiCategory, expected_category)
        assert phi_category == expected_phi_category, f"Expected {entity_type} -> {expected_category}, got {phi_category}"

def test_convert_to_tagged_entities_dict_format(import_modules):
    operator = AHDSSurrogate()
    entities = [
        {
            'entity_type': 'PERSON',
            'start': 0,
            'end': 8,
            'text': 'John Doe',
            'score': 0.9
        },
        {
            'entity_type': 'DATE_TIME',
            'start': 20,
            'end': 30,
            'text': '2024-01-15',
            'score': 0.8
        }
    ]
    tagged_entities = operator._convert_to_tagged_entities(entities)
    assert len(tagged_entities) == 2
    assert tagged_entities[0].offset == 0
    assert tagged_entities[0].length == 8
    assert tagged_entities[1].offset == 20
    assert tagged_entities[1].length == 10

def test_convert_to_tagged_entities_recognizer_result_format(import_modules):
    operator = AHDSSurrogate()
    class MockRecognizerResult:
        def __init__(self, entity_type, start, end, text, score):
            self.entity_type = entity_type
            self.start = start
            self.end = end
            self.text = text
            self.score = score
    entities = [
        MockRecognizerResult('PERSON', 0, 8, 'John Doe', 0.9),
        MockRecognizerResult('DATE_TIME', 20, 30, '2024-01-15', 0.8)
    ]
    tagged_entities = operator._convert_to_tagged_entities(entities)
    assert len(tagged_entities) == 2
    assert tagged_entities[0].offset == 0
    assert tagged_entities[0].length == 8
    assert tagged_entities[1].offset == 20
    assert tagged_entities[1].length == 10

def test_service_error_handling(import_modules):
    operator = AHDSSurrogate()
    params = {
        "endpoint": "https://invalid.endpoint.com",
        "entities": [
            {'entity_type': 'PERSON', 'start': 0, 'end': 8, 'text': 'John Doe', 'score': 0.9}
        ]
    }
    with pytest.raises(InvalidParamError):
        operator.operate("John Doe is a patient", params)

def test_operator_type(import_modules):
    operator = AHDSSurrogate()
    from presidio_anonymizer.operators import OperatorType
    assert operator.operator_type() == OperatorType.Anonymize

@requires_env_vars()
def test_parameter_validation_with_correct_env_var(import_modules):
    operator = AHDSSurrogate()
    original_endpoint = os.getenv("AHDS_ENDPOINT")
    try:
        os.environ["AHDS_ENDPOINT"] = "https://test.endpoint.com"
        params = {
            "entities": [],
            "input_locale": "en-US"
        }
        operator.validate(params)
    finally:
        if original_endpoint:
            os.environ["AHDS_ENDPOINT"] = original_endpoint
        elif "AHDS_ENDPOINT" in os.environ:
            del os.environ["AHDS_ENDPOINT"]

@requires_env_vars()
def test_sdk_with_real_endpoint(import_modules):
    from azure.health.deidentification import DeidentificationClient
    from azure.health.deidentification.models import (
        DeidentificationContent,
        DeidentificationCustomizationOptions,
        SimplePhiEntity,
        TaggedPhiEntities,
        PhiCategory,
        DeidentificationOperationType,
        TextEncodingType,
    )
    from azure.identity import DefaultAzureCredential
    endpoint = os.getenv("AHDS_ENDPOINT")
    if not endpoint:
        pytest.skip("AHDS_ENDPOINT not set in environment")
    credential = DefaultAzureCredential()
    client = DeidentificationClient(endpoint, credential)
    text = "Hello, my name is John Smith."
    tagged_entities = [
        SimplePhiEntity(
            category=PhiCategory.PATIENT,
            offset=18,
            length=10
        )
    ]
    customizations = DeidentificationCustomizationOptions(input_locale="en-US")
    content = DeidentificationContent(
        input_text=text,
        operation_type=DeidentificationOperationType.SURROGATE_ONLY,
        tagged_entities=TaggedPhiEntities(
            encoding=TextEncodingType.CODE_POINT,
            entities=tagged_entities
        ),
        customizations=customizations
    )
    try:
        result = client.deidentify_text(content)
        assert result is not None
        assert result.output_text is not None
        assert len(result.output_text) > 0
        assert result.output_text != text
        print(f"SDK Test - Original:  {text}")
        print(f"SDK Test - Surrogate: {result.output_text}")
    except Exception as e:
        if "DefaultAzureCredential" in str(e) or "authentication" in str(e).lower():
            pytest.skip("Azure authentication not available in test environment")
        elif "Forbidden" in str(e):
            pytest.skip("Azure credentials lack permission to access AHDS service")
        elif "500" in str(e) or "InternalServerError" in str(e):
            pytest.skip("AHDS service temporarily unavailable")
        elif "ApiVersionUnsupported" in str(e):
            pytest.skip("API version not supported by AHDS service")
        else:
            raise

@requires_env_vars()
def test_different_locales_surrogate_only(import_modules):
    from azure.health.deidentification import DeidentificationClient
    from azure.health.deidentification.models import (
        DeidentificationContent,
        DeidentificationCustomizationOptions,
        DeidentificationOperationType,
        DeidentificationResult,
        PhiCategory,
        SimplePhiEntity,
        TaggedPhiEntities,
        TextEncodingType,
    )
    from azure.identity import DefaultAzureCredential
    endpoint = os.environ["AHDS_ENDPOINT"]
    credential = DefaultAzureCredential()
    client = DeidentificationClient(endpoint, credential)
    text = "Patient Marie Dupont was seen on 15/01/2024."
    tagged_entities = TaggedPhiEntities(
        encoding=TextEncodingType.CODE_POINT,
        entities=[
            SimplePhiEntity(category=PhiCategory.PATIENT, offset=8, length=12),
            SimplePhiEntity(category=PhiCategory.DATE, offset=34, length=10),
        ],
    )
    body = DeidentificationContent(
        input_text=text,
        operation_type=DeidentificationOperationType.SURROGATE_ONLY,
        tagged_entities=tagged_entities,
        customizations=DeidentificationCustomizationOptions(input_locale="fr-FR"),
    )
    try:
        result: DeidentificationResult = client.deidentify_text(body)
        assert result is not None
        assert result.output_text is not None
        assert result.output_text != text
        print(f'French Locale Original: "{text}"')
        print(f'French Locale Surrogate: "{result.output_text}"')
    except Exception as e:
        if "DefaultAzureCredential" in str(e) or "authentication" in str(e).lower():
            pytest.skip("Azure authentication not available in test environment")
        elif "Forbidden" in str(e):
            pytest.skip("Azure credentials lack permission to access AHDS service")
        elif "500" in str(e) or "InternalServerError" in str(e):
            pytest.skip("AHDS service temporarily unavailable")
        else:
            raise
