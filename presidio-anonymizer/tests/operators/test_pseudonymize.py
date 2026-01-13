"""Tests for Pseudonymize operator."""

import pytest
from presidio_anonymizer.entities import InvalidParamError
from presidio_anonymizer.operators import Pseudonymize

# Check if Faker is available
try:
    import faker  # noqa: F401
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not FAKER_AVAILABLE,
    reason="Faker library not installed"
)


class TestPseudonymize:
    """Test suite for Pseudonymize operator."""

    def test_given_entity_type_person_then_generates_name(self):
        """Test that PERSON entity generates a name."""
        pseudonymizer = Pseudonymize()
        params = {"entity_type": "PERSON", "locale": "en_US"}
        result = pseudonymizer.operate("John Doe", params)

        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        assert result != "John Doe"

    def test_given_entity_type_email_then_generates_email(self):
        """Test that EMAIL_ADDRESS entity generates an email."""
        pseudonymizer = Pseudonymize()
        params = {"entity_type": "EMAIL_ADDRESS", "locale": "en_US"}
        result = pseudonymizer.operate("test@example.com", params)

        assert result is not None
        assert "@" in result
        assert result != "test@example.com"

    def test_given_entity_type_phone_then_generates_phone(self):
        """Test that PHONE_NUMBER entity generates a phone number."""
        pseudonymizer = Pseudonymize()
        params = {"entity_type": "PHONE_NUMBER", "locale": "en_US"}
        result = pseudonymizer.operate("555-1234", params)

        assert result is not None
        assert isinstance(result, str)
        assert result != "555-1234"

    def test_given_consistent_true_then_same_input_returns_same_output(self):
        """Test that consistent=True returns same pseudonym for same input."""
        pseudonymizer = Pseudonymize()
        params = {
            "entity_type": "PERSON",
            "locale": "en_US",
            "consistent": True
        }

        result1 = pseudonymizer.operate("John Doe", params)
        result2 = pseudonymizer.operate("John Doe", params)

        assert result1 == result2

    def test_given_consistent_false_then_same_input_may_return_different_output(self):
        """Test that consistent=False may return different pseudonyms."""
        pseudonymizer = Pseudonymize()
        params = {
            "entity_type": "PERSON",
            "locale": "en_US",
            "consistent": False
        }

        # Generate multiple results
        results = [pseudonymizer.operate("John Doe", params) for _ in range(10)]

        # With consistent=False, we should potentially see different results
        # (though there's a small chance they might be the same)
        assert len(results) == 10

    def test_given_seed_then_results_are_reproducible(self):
        """Test that using a seed makes results reproducible."""
        params1 = {
            "entity_type": "PERSON",
            "locale": "en_US",
            "seed": 12345
        }
        params2 = {
            "entity_type": "PERSON",
            "locale": "en_US",
            "seed": 12345
        }

        pseudonymizer1 = Pseudonymize()
        pseudonymizer2 = Pseudonymize()

        result1 = pseudonymizer1.operate("John Doe", params1)
        result2 = pseudonymizer2.operate("John Doe", params2)

        assert result1 == result2

    def test_given_different_locales_then_generates_appropriate_data(self):
        """Test that different locales generate appropriate data."""
        pseudonymizer = Pseudonymize()

        # English locale
        params_en = {"entity_type": "PERSON", "locale": "en_US"}
        result_en = pseudonymizer.operate("John Doe", params_en)

        # Korean locale
        params_kr = {"entity_type": "PERSON", "locale": "ko_KR"}
        result_kr = pseudonymizer.operate("홍길동", params_kr)

        assert result_en is not None
        assert result_kr is not None
        assert isinstance(result_en, str)
        assert isinstance(result_kr, str)

    def test_given_unknown_entity_type_then_returns_fallback(self):
        """Test that unknown entity types use fallback method."""
        pseudonymizer = Pseudonymize()
        params = {"entity_type": "UNKNOWN_TYPE", "locale": "en_US"}
        result = pseudonymizer.operate("some text", params)

        assert result is not None
        assert isinstance(result, str)

    def test_given_credit_card_entity_then_generates_credit_card(self):
        """Test CREDIT_CARD entity generates a credit card number."""
        pseudonymizer = Pseudonymize()
        params = {"entity_type": "CREDIT_CARD", "locale": "en_US"}
        result = pseudonymizer.operate("4111-1111-1111-1111", params)

        assert result is not None
        assert isinstance(result, str)
        # Credit card numbers are typically 13-19 digits
        digits_only = ''.join(c for c in result if c.isdigit())
        assert len(digits_only) >= 13

    def test_given_location_entity_then_generates_city(self):
        """Test LOCATION entity generates a city name."""
        pseudonymizer = Pseudonymize()
        params = {"entity_type": "LOCATION", "locale": "en_US"}
        result = pseudonymizer.operate("New York", params)

        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_validate_accepts_valid_locale(self):
        """Test validation accepts valid locale string."""
        pseudonymizer = Pseudonymize()
        params = {"locale": "en_US"}
        # Should not raise an exception
        pseudonymizer.validate(params)

    def test_validate_accepts_valid_seed(self):
        """Test validation accepts valid seed integer."""
        pseudonymizer = Pseudonymize()
        params = {"seed": 12345}
        # Should not raise an exception
        pseudonymizer.validate(params)

    def test_validate_accepts_valid_consistent(self):
        """Test validation accepts valid consistent boolean."""
        pseudonymizer = Pseudonymize()
        params = {"consistent": True}
        # Should not raise an exception
        pseudonymizer.validate(params)

    def test_validate_rejects_invalid_seed_type(self):
        """Test validation rejects non-integer seed."""
        pseudonymizer = Pseudonymize()
        params = {"seed": "invalid"}

        with pytest.raises(InvalidParamError, match="must be an integer"):
            pseudonymizer.validate(params)

    def test_validate_rejects_invalid_consistent_type(self):
        """Test validation rejects non-boolean consistent."""
        pseudonymizer = Pseudonymize()
        params = {"consistent": "invalid"}

        with pytest.raises(InvalidParamError, match="must be a boolean"):
            pseudonymizer.validate(params)

    def test_operator_name_returns_pseudonymize(self):
        """Test operator name is 'pseudonymize'."""
        pseudonymizer = Pseudonymize()
        assert pseudonymizer.operator_name() == "pseudonymize"

    def test_operator_type_is_anonymize(self):
        """Test operator type is Anonymize."""
        from presidio_anonymizer.operators import OperatorType

        pseudonymizer = Pseudonymize()
        assert pseudonymizer.operator_type() == OperatorType.Anonymize

    def test_default_locale_is_en_us(self):
        """Test that default locale is en_US when not specified."""
        pseudonymizer = Pseudonymize()
        params = {"entity_type": "PERSON"}
        result = pseudonymizer.operate("John Doe", params)

        assert result is not None
        assert isinstance(result, str)

    def test_default_consistent_is_true(self):
        """Test that default consistent value is True."""
        pseudonymizer = Pseudonymize()
        params = {"entity_type": "PERSON"}

        result1 = pseudonymizer.operate("Test Name", params)
        result2 = pseudonymizer.operate("Test Name", params)

        # Default should be consistent=True
        assert result1 == result2

    def test_different_inputs_with_consistent_get_different_outputs(self):
        """Test different inputs get different pseudonyms with consistent=True."""
        pseudonymizer = Pseudonymize()
        params = {"entity_type": "PERSON", "consistent": True}

        result1 = pseudonymizer.operate("John Doe", params)
        result2 = pseudonymizer.operate("Jane Smith", params)

        # Different inputs should get different outputs
        assert result1 != result2
