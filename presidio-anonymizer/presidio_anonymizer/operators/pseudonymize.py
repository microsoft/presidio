"""Generate realistic fake data while preserving format and consistency."""

from typing import Dict

from presidio_anonymizer.entities import InvalidParamError
from presidio_anonymizer.operators import Operator, OperatorType
from presidio_anonymizer.services.validators import validate_parameter


class Pseudonymize(Operator):
    """
    Pseudonymize PII entities using Faker library.

    Generates realistic fake data based on entity type with support for:
    - Multiple locales
    - Consistent mapping (same input = same output)
    - Reproducible results via seed
    """

    LOCALE = "locale"
    SEED = "seed"
    CONSISTENT = "consistent"

    # Entity type to Faker method mapping
    ENTITY_MAPPINGS = {
        "PERSON": "name",
        "EMAIL_ADDRESS": "email",
        "PHONE_NUMBER": "phone_number",
        "LOCATION": "city",
        "DATE_TIME": "date",
        "CREDIT_CARD": "credit_card_number",
        "URL": "url",
        "IP_ADDRESS": "ipv4",
        "US_SSN": "ssn",
        "IBAN_CODE": "iban",
        "NRP": "country",
        "ORGANIZATION": "company",
    }

    def __init__(self):
        """Initialize Pseudonymize operator."""
        self._faker_instance = None
        self._mapping_cache = {}

    def operate(self, text: str = None, params: Dict = None) -> str:
        """
        Generate pseudonymized value using Faker.

        :param text: The original text to pseudonymize
        :param params: Parameters including:
            - locale: Faker locale (default: "en_US")
            - seed: Random seed for reproducibility (optional)
            - consistent: If True, same input returns same output (default: True)
            - entity_type: Type of entity being anonymized
        :return: Pseudonymized text
        """
        try:
            from faker import Faker
        except ImportError:
            raise InvalidParamError(
                "Faker library is required for pseudonymize operator. "
                "Install it with: pip install faker"
            )

        locale = params.get(self.LOCALE, "en_US")
        seed = params.get(self.SEED)
        consistent = params.get(self.CONSISTENT, True)
        entity_type = params.get("entity_type", "PERSON")

        # Use consistent mapping if enabled
        if consistent:
            cache_key = f"{locale}:{entity_type}:{text}"
            if cache_key in self._mapping_cache:
                return self._mapping_cache[cache_key]

        # Create or reuse Faker instance
        if seed is not None:
            # Create new instance with seed for reproducibility
            fake = Faker(locale)
            Faker.seed(seed)
        else:
            # Reuse instance for performance
            if self._faker_instance is None or self._faker_instance.locale != locale:
                self._faker_instance = Faker(locale)
            fake = self._faker_instance

        # Get the appropriate Faker method for the entity type
        faker_method_name = self.ENTITY_MAPPINGS.get(entity_type, "word")

        try:
            faker_method = getattr(fake, faker_method_name)
            pseudonym = str(faker_method())
        except AttributeError:
            # Fallback to random word if method not available
            pseudonym = fake.word()

        # Cache the result if consistency is enabled
        if consistent:
            cache_key = f"{locale}:{entity_type}:{text}"
            self._mapping_cache[cache_key] = pseudonym

        return pseudonym

    def validate(self, params: Dict = None) -> None:
        """
        Validate pseudonymize parameters.

        :param params: Parameters to validate
        """
        locale = params.get(self.LOCALE)
        if locale is not None:
            validate_parameter(locale, self.LOCALE, str)

        seed = params.get(self.SEED)
        if seed is not None and not isinstance(seed, int):
            raise InvalidParamError(
                f"Invalid input, {self.SEED} must be an integer"
            )

        consistent = params.get(self.CONSISTENT)
        if consistent is not None and not isinstance(consistent, bool):
            raise InvalidParamError(
                f"Invalid input, {self.CONSISTENT} must be a boolean"
            )

    def operator_name(self) -> str:
        """Return operator name."""
        return "pseudonymize"

    def operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.Anonymize
