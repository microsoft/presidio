"""Tests for the AHDS Surrogate operator."""

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
class TestAHDSSurrogate:
    """Test AHDS Surrogate operator."""
    
    def test_operator_name(self, import_modules):
        """Test operator name."""
        operator = AHDSSurrogate()
        assert operator.operator_name() == "surrogate"

    @requires_env_vars()
    def test_surrogate_only_operation_sample_pattern(self, import_modules):
        """Test SurrogateOnly operation using the exact pattern from the sample."""
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

        # Define the entities to be surrogated - targeting "John Smith" at position 18-28
        tagged_entities = TaggedPhiEntities(
            encoding=TextEncodingType.CODE_POINT,
            entities=[SimplePhiEntity(category=PhiCategory.PATIENT, offset=18, length=10)],
        )

        # Use SurrogateOnly operation with input locale specification
        body = DeidentificationContent(
            input_text="Hello, my name is John Smith.",
            operation_type=DeidentificationOperationType.SURROGATE_ONLY,
            tagged_entities=tagged_entities,
            customizations=DeidentificationCustomizationOptions(
                input_locale="en-US"  # Specify input text locale for better PHI detection
            ),
        )

        try:
            result: DeidentificationResult = client.deidentify_text(body)
            
            # Verify the operation worked
            assert result is not None
            assert result.output_text is not None
            assert len(result.output_text) > 0
            
            # The output should be different from input (surrogates applied)
            assert result.output_text != body.input_text
            
            print(f'Original Text:        "{body.input_text}"')
            print(f'Surrogate Only Text:  "{result.output_text}"')
            
        except Exception as e:
            # Handle authentication and service errors gracefully in tests
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
    def test_multiple_entities_surrogate_only(self, import_modules):
        """Test SurrogateOnly operation with multiple entity types."""
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

        # Test text with multiple entity types
        text = "Patient John Doe was seen by Dr. Smith on 2024-01-15. Contact: john.doe@email.com or 555-123-4567."
        
        # Define multiple entities for surrogate replacement
        tagged_entities = TaggedPhiEntities(
            encoding=TextEncodingType.CODE_POINT,
            entities=[
                SimplePhiEntity(category=PhiCategory.PATIENT, offset=8, length=8),    # "John Doe"
                SimplePhiEntity(category=PhiCategory.DOCTOR, offset=29, length=9),    # "Dr. Smith"
                SimplePhiEntity(category=PhiCategory.DATE, offset=42, length=10),     # "2024-01-15"
                SimplePhiEntity(category=PhiCategory.EMAIL, offset=63, length=17),    # "john.doe@email.com"
                SimplePhiEntity(category=PhiCategory.PHONE, offset=84, length=12),    # "555-123-4567"
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

    def test_operation_type_is_surrogate_only(self, import_modules):
        """Test that the operator uses the correct SURROGATE_ONLY operation type."""
        from azure.health.deidentification.models import DeidentificationOperationType
        
        # Verify that the operation type constant exists and has the right value
        assert hasattr(DeidentificationOperationType, 'SURROGATE_ONLY')
        assert DeidentificationOperationType.SURROGATE_ONLY == "SurrogateOnly"
    
    def test_phi_categories_available(self, import_modules):
        """Test that required PHI categories are available."""
        from azure.health.deidentification.models import PhiCategory
        
        # Test that common categories we use are available
        required_categories = ['PATIENT', 'DOCTOR', 'DATE', 'PHONE', 'EMAIL']
        
        for category_name in required_categories:
            assert hasattr(PhiCategory, category_name), f"PhiCategory.{category_name} not available"
    
    @requires_env_vars()
    def test_operator_integration_with_ahds_client(self, import_modules):
        """Test the AHDSSurrogate operator integration with real AHDS service."""
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
    def test_integration_with_real_service(self, import_modules):
        """Integration test with real AHDS service."""
        operator = AHDSSurrogate()
        
        # Sample text with PII
        text = "Patient John Doe was seen by Dr. Smith on 2024-01-15"
        
        # Mock entity results (what would come from analyzer)
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
            # If service is unavailable, this is expected in CI
            if "Forbidden" in str(e):
                pytest.skip("Azure credentials lack permission to access AHDS service")
            elif "500" in str(e) or "InternalServerError" in str(e):
                pytest.skip("AHDS service temporarily unavailable")
            else:
                raise
    
    def test_entity_mapping_to_phi_categories(self, import_modules):
        """Test entity type mapping to PHI categories."""
        operator = AHDSSurrogate()
        
        # Test various entity types with expected mappings
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
    
    def test_convert_to_tagged_entities_dict_format(self, import_modules):
        """Test conversion of dict format entities to tagged entities."""
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
    
    def test_convert_to_tagged_entities_recognizer_result_format(self, import_modules):
        """Test conversion of RecognizerResult format entities to tagged entities."""
        operator = AHDSSurrogate()
        
        # Mock RecognizerResult objects
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
    
    def test_service_error_handling(self, import_modules):
        """Test error handling for service errors."""
        operator = AHDSSurrogate()
        
        # Test with invalid endpoint to trigger error handling
        params = {
            "endpoint": "https://invalid.endpoint.com",
            "entities": [
                {'entity_type': 'PERSON', 'start': 0, 'end': 8, 'text': 'John Doe', 'score': 0.9}
            ]
        }
        
        with pytest.raises(InvalidParamError):
            operator.operate("John Doe is a patient", params)
    
    def test_operator_type(self, import_modules):
        """Test operator type."""
        operator = AHDSSurrogate()
        from presidio_anonymizer.operators import OperatorType
        assert operator.operator_type() == OperatorType.Anonymize
    
    @requires_env_vars()
    def test_parameter_validation_with_correct_env_var(self, import_modules):
        """Test parameter validation using the correct environment variable."""
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
    def test_sdk_with_real_endpoint(self, import_modules):
        """Test SDK functionality with real AHDS endpoint."""
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
                offset=18,  # "John Smith"
                length=10
            )
        ]
        
        customizations = DeidentificationCustomizationOptions(
            input_locale="en-US"
        )
        
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
    def test_different_locales_surrogate_only(self, import_modules):
        """Test SurrogateOnly operation with different locale settings."""
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

        # Test with different locale
        text = "Patient Marie Dupont was seen on 15/01/2024."
        
        tagged_entities = TaggedPhiEntities(
            encoding=TextEncodingType.CODE_POINT,
            entities=[
                SimplePhiEntity(category=PhiCategory.PATIENT, offset=8, length=12),  # "Marie Dupont"
                SimplePhiEntity(category=PhiCategory.DATE, offset=34, length=10),    # "15/01/2024"
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
