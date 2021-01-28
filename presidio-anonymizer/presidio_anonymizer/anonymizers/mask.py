"""Mask some or all given text entity PII with given character."""
from presidio_anonymizer.anonymizers import Anonymizer
from presidio_anonymizer.anonymizers.validators import validate_parameter
from presidio_anonymizer.entities import InvalidParamException


class Mask(Anonymizer):
    """Mask the given text with given value."""

    def anonymize(self, text: str = None, params: dict = None) -> str:
        """
        Mask a given amount of text with a given character.

        :param text: the text to be masked
        :param params:
            masking_char: The character to be masked with
            chars_to_mask: The amount of characters to mask
            from_end: Whether to mask the text from it's end
        :return: the masked text
        """
        effective_chars_to_mask = self._get_effective_chars_to_mask(
            text, params.get("chars_to_mask")
        )
        from_end = params.get("from_end")
        masking_char = params.get("masking_char")
        return self._get_anonymized_text(
            text, effective_chars_to_mask, from_end, masking_char
        )

    def validate(self, params: dict = None) -> None:
        """
        Validate the parameters for mask.

        :param params:
            masking_char: The character to be masked with
            chars_to_mask: The amount of characters to mask
            from_end: Whether to mask the text from it's end
        """
        masking_char = params.get("masking_char")
        validate_parameter(masking_char, "masking_char", str)
        if len(masking_char) > 1:
            raise InvalidParamException(
                f"Invalid input, masking_char must be a character"
            )

        validate_parameter(params.get("chars_to_mask"), "chars_to_mask", int)
        validate_parameter(params.get("from_end"), "from_end", bool)

    @staticmethod
    def _get_effective_chars_to_mask(text, chars_to_mask):
        return min(len(text), chars_to_mask) if chars_to_mask > 0 else 0

    @staticmethod
    def _get_anonymized_text(text, chars_to_mask, from_end, masking_char):
        if not from_end:
            return masking_char * chars_to_mask + text[chars_to_mask:]
        else:
            mask_from_index = len(text) - chars_to_mask
            return text[:mask_from_index] + masking_char * chars_to_mask
