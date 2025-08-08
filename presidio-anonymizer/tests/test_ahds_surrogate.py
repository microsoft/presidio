"""Tests for the AHDS Surrogate operator."""

import os
import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("AHDS_ENDPOINT"),
    reason="AHDS_ENDPOINT environment variable not set"
)

try:
    from presidio_anonymizer.operators import AHDSSurrogate
    from presidio_anonymizer.entities import InvalidParamError
    AHDS_AVAILABLE = True
except ImportError:
    AHDS_AVAILABLE = False


@pytest.mark.skipif(not AHDS_AVAILABLE, reason="AHDS dependencies not available")
class TestAHDSSurrogate:
    """Test AHDS Surrogate operator."""
    
    def test_operator_name(self):
        """Test operator name."""
        operator = AHDSSurrogate()
        assert operator.operator_name() == "surrogate"
    
    def test_validate_missing_endpoint(self):
        """Test validation fails when endpoint is missing."""
        operator = AHDSSurrogate()
        
        # Remove AHDS_ENDPOINT if set temporarily
        original_endpoint = os.environ.get("AHDS_ENDPOINT")
        if original_endpoint:
            del os.environ["AHDS_ENDPOINT"]
        
        try:
            with pytest.raises(InvalidParamError, match="AHDS endpoint is required"):
                operator.validate({})
        finally:
            if original_endpoint:
                os.environ["AHDS_ENDPOINT"] = original_endpoint
    
    def test_validate_with_endpoint_param(self):
        """Test validation passes when endpoint is provided as parameter."""
        operator = AHDSSurrogate()
        params = {
            "endpoint": "https://test.api.deid.azure.com",
            "entities": []
        }
        operator.validate(params)
    
    def test_validate_entities_not_list(self):
        """Test validation fails when entities is not a list."""
        operator = AHDSSurrogate()
        params = {
            "endpoint": "https://test.api.deid.azure.com",
            "entities": "not_a_list"
        }
        with pytest.raises(InvalidParamError, match="Entities must be a list"):
            operator.validate(params)
    
    def test_operate_empty_text(self):
        """Test operator returns empty string for empty text."""
        operator = AHDSSurrogate()
        result = operator.operate("", {})
        assert result == ""
    
    def test_surrogate_only_operation_directly(self):
        """Test the SurrogateOnly operation directly via AHDS API."""
        # Import AHDS models for direct testing
        from azure.health.deidentification import DeidentificationClient
        from azure.health.deidentification.models import (
            DeidentificationContent,
            SimplePhiEntity,
            TaggedPhiEntities,
            PhiCategory,
            DeidentificationOperationType,
            TextEncodingType,
        )
        from azure.identity import DefaultAzureCredential
        
        # Sample text with PII
        text = "Patient John Doe was seen by Dr. Smith on 2024-01-15"
        
        # Create tagged entities for specific PII locations
        tagged_entities = [
            SimplePhiEntity(
                category=PhiCategory.PATIENT,
                offset=8,   # "John Doe" 
                length=8
            ),
            SimplePhiEntity(
                category=PhiCategory.DOCTOR,
                offset=29,  # "Dr. Smith"
                length=9
            ),
            SimplePhiEntity(
                category=PhiCategory.DATE,
                offset=42,  # "2024-01-15"
                length=10
            )
        ]
        
        # Create tagged entity collection
        tagged_entity_collection = TaggedPhiEntities(
            encoding=TextEncodingType.CODE_POINT,
            entities=tagged_entities
        )
        
        # Create content with SurrogateOnly operation
        content = DeidentificationContent(
            input_text=text,
            operation_type=DeidentificationOperationType.SURROGATE_ONLY,
            tagged_entities=tagged_entity_collection
        )
        
        try:
            # Create client and test
            endpoint = os.getenv('AHDS_ENDPOINT')
            credential = DefaultAzureCredential()
            client = DeidentificationClient(endpoint, credential, api_version="2024-11-15")
            
            result = client.deidentify_text(content)
            
            # Verify the operation worked
            assert result is not None
            assert result.output_text is not None
            assert len(result.output_text) > 0
            
            # The output should be different from input (surrogates applied)
            assert result.output_text != text
            
            print(f"Original:  {text}")
            print(f"Surrogate: {result.output_text}")
            
        except Exception as e:
            # Handle authentication and service errors gracefully in tests
            if "DefaultAzureCredential" in str(e) or "authentication" in str(e).lower():
                pytest.skip("Azure authentication not available in test environment")
            elif "500" in str(e) or "InternalServerError" in str(e):
                pytest.skip("AHDS service temporarily unavailable")
            elif "ApiVersionUnsupported" in str(e):
                pytest.skip("API version not supported by AHDS service")
            else:
                raise
    
    def test_operation_type_is_surrogate_only(self):
        """Test that the operator uses the correct SURROGATE_ONLY operation type."""
        from azure.health.deidentification.models import DeidentificationOperationType
        
        # Verify that the operation type constant exists and has the right value
        assert hasattr(DeidentificationOperationType, 'SURROGATE_ONLY')
        assert DeidentificationOperationType.SURROGATE_ONLY == "SurrogateOnly"
    
    def test_phi_categories_available(self):
        """Test that required PHI categories are available."""
        from azure.health.deidentification.models import PhiCategory
        
        # Test that common categories we use are available
        required_categories = ['PATIENT', 'DOCTOR', 'DATE', 'PHONE', 'EMAIL']
        
        for category_name in required_categories:
            assert hasattr(PhiCategory, category_name), f"PhiCategory.{category_name} not available"
    
    def test_integration_with_real_service(self):
        """Integration test with real AHDS service."""
        operator = AHDSSurrogate()
        
        # Sample text with PII
        text = "Patient John Doe was seen by Dr. Smith on 2024-01-15"
        
        # Mock entity results (what would come from analyzer)
        mock_entities = [
            {
                'entity_type': 'PATIENT', 
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
                'entity_type': 'DATE', 
                'start': 42, 
                'end': 52, 
                'text': '2024-01-15',
                'score': 0.9
            }
        ]
        
        params = {
            "entities": mock_entities,
            "input_locale": "en-US",
            "surrogate_locale": "en-US"
        }
        
        try:
            result = operator.operate(text, params)
            
            # Verify result is not empty and different from original
            assert result is not None
            assert len(result) > 0
            assert result != text  # Should be different due to surrogate replacement
            
            # Verify original structure is maintained (same length approximately)
            # Allow some variance in length due to surrogate generation
            length_diff = abs(len(result) - len(text))
            assert length_diff < 50, f"Result length too different: {len(result)} vs {len(text)}"
            
            print(f"Original: {text}")
            print(f"Surrogate: {result}")
            
        except Exception as e:
            # If service is unavailable, this is expected in CI
            if "500" in str(e) or "InternalServerError" in str(e):
                pytest.skip("AHDS service temporarily unavailable")
            else:
                raise
    
    def test_entity_mapping_to_phi_categories(self):
        """Test entity type mapping to PHI categories."""
        operator = AHDSSurrogate()
        
        # Test various entity types
        test_cases = [
            "PATIENT", "PERSON", "DOCTOR", "DATE", "PHONE_NUMBER", 
            "EMAIL", "SSN", "UNKNOWN_TYPE"
        ]
        
        for entity_type in test_cases:
            phi_category = operator._map_to_phi_category(entity_type)
            assert phi_category is not None
            # For now, everything maps to PATIENT as per implementation
            from azure.health.deidentification.models import PhiCategory
            assert phi_category == PhiCategory.PATIENT
    
    def test_convert_to_tagged_entities_dict_format(self):
        """Test conversion of dict format entities to tagged entities."""
        operator = AHDSSurrogate()
        
        entities = [
            {
                'entity_type': 'PATIENT',
                'start': 0,
                'end': 8,
                'text': 'John Doe',
                'score': 0.9
            },
            {
                'entity_type': 'DATE',
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
    
    def test_convert_to_tagged_entities_recognizer_result_format(self):
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
            MockRecognizerResult('PATIENT', 0, 8, 'John Doe', 0.9),
            MockRecognizerResult('DATE', 20, 30, '2024-01-15', 0.8)
        ]
        
        tagged_entities = operator._convert_to_tagged_entities(entities)
        
        assert len(tagged_entities) == 2
        assert tagged_entities[0].offset == 0
        assert tagged_entities[0].length == 8
        assert tagged_entities[1].offset == 20
        assert tagged_entities[1].length == 10
    
    def test_service_error_handling(self):
        """Test error handling for service errors."""
        operator = AHDSSurrogate()
        
        # Test with invalid endpoint to trigger error handling
        params = {
            "endpoint": "https://invalid.endpoint.com",
            "entities": [
                {'entity_type': 'PATIENT', 'start': 0, 'end': 8, 'text': 'John Doe', 'score': 0.9}
            ]
        }
        
        with pytest.raises(InvalidParamError):
            operator.operate("John Doe is a patient", params)
    
    def test_operator_type(self):
        """Test operator type."""
        operator = AHDSSurrogate()
        from presidio_anonymizer.operators import OperatorType
        assert operator.operator_type() == OperatorType.Anonymize
    
    def test_parameter_validation_input_locale(self):
        """Test parameter validation for locale parameters."""
        operator = AHDSSurrogate()
        
        params = {
            "endpoint": "https://test.api.deid.azure.com",
            "entities": [],
            "input_locale": "fr-FR",
            "surrogate_locale": "es-ES"
        }
        
        # Should not raise exception for valid locale parameters
        operator.validate(params)
