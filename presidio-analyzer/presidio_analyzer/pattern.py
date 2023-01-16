import json
from typing import Dict


class Pattern:
    """
    A class that represents a regex pattern.

    :param name: the name of the pattern
    :param regex: the regex pattern to detect
    :param score: the pattern's strength (values varies 0-1)
    """

    def __init__(self, name: str, regex: str, score: float):

        self.name = name
        self.regex = regex
        self.score = score

    def to_dict(self) -> Dict:
        """
        Turn this instance into a dictionary.

        :return: a dictionary
        """
        return_dict = {"name": self.name, "score": self.score, "regex": self.regex}
        return return_dict

    @classmethod
    def from_dict(cls, pattern_dict: Dict) -> "Pattern":
        """
        Load an instance from a dictionary.

        :param pattern_dict: a dictionary holding the pattern's parameters
        :return: a Pattern instance
        """
        return cls(**pattern_dict)

    def __repr__(self):
        """Return string representation of instance."""
        return json.dumps(self.to_dict())

    def __str__(self):
        """Return string representation of instance."""
        return json.dumps(self.to_dict())
