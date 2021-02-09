"""Replaces the PII text entity with new string."""
from presidio_anonymizer.anonymizers import Anonymizer
from presidio_anonymizer.anonymizers.validators import validate_type


class Replace(Anonymizer):
    """Receives new text to replace old PII text entity with."""

    NEW_VALUE = "new_value"

    def anonymize(self, text: str = None, params: dict = None) -> str:
        """:return: new_value."""
        new_val = params.get(self.NEW_VALUE)
        if not new_val:
            return f"<{params.get('entity_type')}>"
        return new_val

    def validate(self, params: dict = None) -> None:
        """Validate the new value is string."""
        validate_type(params.get(self.NEW_VALUE), self.NEW_VALUE, str)
        pass

    def anonymizer_name(self) -> str:
        """Return anonymizer name."""
        return "replace"
