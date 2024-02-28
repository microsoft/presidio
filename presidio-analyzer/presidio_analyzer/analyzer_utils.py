from typing import List, Tuple


class PresidioAnalyzerUtils:
    """
    Utility functions for Presidio Analyzer.

    The class provides a bundle of utility functions that help centralizing the
    logic for re-usability and maintainability
    """

    @staticmethod
    def is_palindrome(text: str, case_insensitive: bool = False):
        """
        Validate if input text is a true palindrome.

        :param text: input text string to check for palindrome
        :param case_insensitive: optional flag to check palindrome with no case
        :return: True / False
        """
        palindrome_text = text
        if case_insensitive:
            palindrome_text = palindrome_text.replace(" ", "").lower()
        return palindrome_text == palindrome_text[::-1]

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

    @staticmethod
    def is_verhoeff_number(input_number: int):
        """
        Check if the input number is a true verhoeff number.

        :param input_number:
        :return:
        """
        __d__ = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
            [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
            [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
            [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
            [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
            [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
            [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
            [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
            [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
        ]
        __p__ = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
            [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
            [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
            [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
            [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
            [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
            [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
        ]
        __inv__ = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]

        c = 0
        inverted_number = list(map(int, reversed(str(input_number))))
        for i in range(len(inverted_number)):
            c = __d__[c][__p__[i % 8][inverted_number[i]]]
        return __inv__[c] == 0
