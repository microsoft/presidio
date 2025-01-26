from typing import List, Tuple


class ValidationUtils:
    """
    Utility functions for Presidio Analyzer.

    The class provides a bundle of utility functions that help centralizing the
    logic for re-usability and maintainability
    """

    @staticmethod
    def sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        """
        Cleanse the input string of the replacement pairs specified as argument.

        :param text: input string
        :param replacement_pairs: pairs of what has to be replaced with which value
        :return: cleansed string
        """
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text
