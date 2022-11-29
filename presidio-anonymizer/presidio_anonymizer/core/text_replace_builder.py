"""Handles the original text and creates a new one according to changes requests."""
import logging

from presidio_anonymizer.entities import InvalidParamException


class TextReplaceBuilder:
    """Creates new text according to users request."""

    def __init__(self, original_text: str):
        self.logger = logging.getLogger("presidio-anonymizer")
        self.output_text = original_text
        self.original_text = original_text
        self.text_len = len(original_text)
        self.last_replacement_index = self.text_len

    def get_text_in_position(self, start: int, end: int) -> str:
        """
        Get part of the text inside the original text.

        :param start: start position of inner text
        :param end: end position of inner text
        :return: str - part of the original text
        """
        self.__validate_position_in_text(start, end)
        return self.original_text[start:end]

    def replace_text_get_insertion_index(
        self, replacement_text: str, start: int, end: int
    ) -> int:
        """
        Replace text in a specific position with the text.

        :param replacement_text: new text to replace the old text according to indices
        :param start: the startpoint to replace the text
        :param end: the endpoint to replace the text
        :return: The index of inserted text
        """
        end_of_text_index = min(end, self.last_replacement_index)
        self.last_replacement_index = start

        before_text = self.output_text[:start]
        after_text = self.output_text[end_of_text_index:]
        self.output_text = before_text + replacement_text + after_text

        # The replace algorithm is replacing the text from end to start.
        # calculate and return the start point from the end.
        return len(after_text) + len(replacement_text)

    def __validate_position_in_text(self, start: int, end: int):
        """Validate the start and end position match the text length."""
        if self.text_len < start or end > self.text_len:
            err_msg = (
                f"Invalid analyzer result, start: {start} and end: "
                f"{end}, while text length is only {self.text_len}."
            )
            raise InvalidParamException(err_msg)
