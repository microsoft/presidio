"""Handles the original text and creates a new one according to changes requests."""
from presidio_anonymizer.entities import InvalidParamException


# TODO awful name! - PR people any ideas?
class AnonymizedTextBuilder:
    """Creates new text according to users request."""

    def __init__(self,
                 original_text: str):
        self.original_text = original_text
        self.output_text = original_text
        self.text_len = len(original_text)
        self.last_replacement_point = self.text_len

    def get_text_in_position(self, start: int, end: int):
        """
        Validate and get part of the text inside the original text.

        :param start: start position of inner text
        :param end: end position of inner text
        :return: str - part of the original text
        """
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
