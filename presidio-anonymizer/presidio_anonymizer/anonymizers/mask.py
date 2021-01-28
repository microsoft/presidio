"""Mask some or all given text entity PII with given character."""
from presidio_anonymizer.anonymizers import Anonymizer
from presidio_anonymizer.anonymizers.validators import validate_parameter
from presidio_anonymizer.entities import InvalidParamException


class Mask(Anonymizer):
    """Mask the given text with given value."""

    def anonymize(self, original_text: str = None, params: dict = None) -> str:
        """
        Anonymize a given amount of text with a given character.

        :return: The given text masked as requested
        """
        effective_chars_to_mask = self._get_effective_chars_to_mask(
            original_text, params.get("effective_chars_to_mask")
        )
        from_end = params.get("from_end")
        masking_char = params.get("masking_char")
        return self._get_anonymized_text(
            original_text, effective_chars_to_mask, from_end, masking_char
        )

    def validate(self, params: dict = None) -> None:
        """TODO: docstring."""
        masking_char = params.get("masking_char")
        validate_parameter(masking_char, "masking_char", str)
        if not len(masking_char) > 1:
            raise InvalidParamException(
                f"Invalid input, masking_char must be a character"
            )

        validate_parameter(params.get("chars_to_mask"), "chars_to_mask", int)
        validate_parameter(params.get("from_end"), "from_end", bool)

    @staticmethod
    def _get_effective_chars_to_mask(original_text, chars_to_mask):
        return min(len(original_text), chars_to_mask) if chars_to_mask > 0 else 0

    @staticmethod
    def _get_anonymized_text(original_text, chars_to_mask, from_end, masking_char):
        if not from_end:
            return masking_char * chars_to_mask + original_text[chars_to_mask:]
        else:
            mask_from_index = len(original_text) - chars_to_mask
            return original_text[:mask_from_index] + masking_char * chars_to_mask
