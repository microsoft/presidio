"""Handles the original text and creates a new one according to changes requests."""
import logging

from presidio_anonymizer.entities import InvalidParamException


class AnonymizedTextBuilder:
    """Creates new text according to users request."""

    def __init__(self,
                 original_text: str):
        self.logger = logging.getLogger("presidio-anonymizer")
        self.__validate_text_not_empty(original_text)
        self.output_text = original_text
        self.text_len = len(original_text)
        self.last_replacement_point = self.text_len

    def __validate_text_not_empty(self, text: str):
        if not text:
            self.logger.debug("invalid input, json is missing text field")
            raise InvalidParamException("Invalid input, text can not be empty")

    def get_text_in_position(self, start: int, end: int) -> str:
        """
        Get part of the text inside the original text.

        :param start: start position of inner text
        :param end: end position of inner text
        :return: str - part of the original text
        """
        self.__validate_position_in_text(start, end)
        return self.output_text[start: end]

    def replace_text(self, anonymized_text: str, start: int, end: int):
        """
        Replace text in a specific position with the anonymized text.

        :param anonymized_text:
        :param start: the startpoint to replace the text
        :param end: the endpoint to replace the text
        :return:
        """
        end_of_text = min(end, self.last_replacement_point)
        self.last_replacement_point = start

        self.output_text = self.output_text[
                           : start] + anonymized_text + self.output_text[end_of_text:]

    def __validate_position_in_text(self, start: int, end: int):
        """Validate the start and end position match the text length."""
        if self.text_len < start or end > self.text_len:
            err_msg = f"Invalid analyzer result, start: {start} and end: " \
                      f"{end}, while text length is only {self.text_len}."
            raise InvalidParamException(
                err_msg)
