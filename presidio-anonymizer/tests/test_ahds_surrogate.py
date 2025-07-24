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
    
    # Note: Integration tests with actual AHDS service will go here
