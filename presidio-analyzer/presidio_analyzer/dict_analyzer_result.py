from dataclasses import dataclass
from typing import List, Union

from presidio_analyzer import RecognizerResult


@dataclass
class DictAnalyzerResult:
    """
    Data class for holding the output of the Presidio Analyzer on dictionaries.

    :param key: key in dictionary
    :param value: value to run analysis on (either string or list of strings)
    :param recognizer_results: Analyzer output for one value
    (either list of recognizer results if the input is one string,
     or a list of list of recognizer results, if the input is a list of strings.
    """

    key: str
    value: Union[str, List[str]]
    recognizer_results: Union[List[RecognizerResult], List[List[RecognizerResult]]]
