"""
AnalyzerResult is the exact copy of the recognizer result.

Represents the findings of detected entity.
"""
import logging
from typing import Dict

from presidio_anonymizer.entities import InvalidParamException


class AnalyzerResult:
    """
    AnalyzerResult is the output of the analyze process.

    Validate and compare an recognizer result object.
    """

    logger = logging.getLogger("presidio-anonymizer")

    @classmethod
    def from_json(cls, data: Dict):
        """
        Create AnalyzerResult from json.

        :param data: e.g. {
            "start": 24,
            "end": 32,
            "score": 0.8,
            "entity_type": "NAME"
        }
        :return: AnalyzerResult
        """
        score = data.get("score")
        entity_type = data.get("entity_type")
        start = data.get("start")
        end = data.get("end")
        return cls(entity_type, start, end, score)

    def __init__(self, entity_type: str, start: int, end: int, score: float):
        self.score = score
        self.entity_type = entity_type
        self.start = start
        self.end = end
        self.__validate_fields()

    def contains(self, other):
        """
        Check if one result is contained or equal to another result.

        :param other: another analyzer_result
        :return: bool
        """
        return self.start <= other.start and self.end >= other.end

    def equal_indices(self, other):
        """
        Check if the indices are equal between two results.

        :param other: another analyzer_result
        :return:
        """
        return self.start == other.start and self.end == other.end

    def __gt__(self, other):
        """
        Check if one result is greater by using the results indices in the text.

        :param other: another analyzer_result
        :return: bool
        """
        if self.start == other.start:
            return self.end > other.end
        return self.start > other.start

    def __eq__(self, other):
        """
        Check two results are equal by using all class fields.

        :param other: another analyzer_result
        :return: bool
        """
        equal_type = self.entity_type == other.entity_type
        equal_score = self.score is other.score
        return self.equal_indices(other) and equal_type and equal_score

    def __hash__(self):
        """
        Hash the result data by using all class fields.

        :return: int
        """
        return hash(
            f"{str(self.start)} {str(self.end)} {str(self.score)} {self.entity_type}")

    def __str__(self):
        """Analyzer_result class data to string."""
        return f"start: {str(self.start)}, end: {str(self.end)}, " \
               f"score: {str(self.score)}, entity_type: {self.entity_type}"

    def has_conflict(self, other):
        """
        Check if two analyzer results are conflicted or not.

        I have a conflict if:
        1. My indices are the same as the other and my score is lower.
        2. If my indices are contained in another.

        :param other: AnalyzerResult
        :return:
        """
        if self.equal_indices(other):
            return self.score <= other.score
        return other.contains(self)

    def __validate_fields(self):
        if self.start is None:
            self.__validate_field("start")
        if self.end is None:
            self.__validate_field("end")
        if self.entity_type is None:
            self.__validate_field("entity_type")
        if self.score is None:
            self.__validate_field("score")
        if self.start < 0 or self.end < 0:
            raise InvalidParamException(
                f"Invalid input, analyzer result start and end must be positive")
        if self.start >= self.end:
            raise InvalidParamException(
                f"Invalid input, analyzer result start index '{self.start}' "
                f"must be smaller than end index '{self.end}'")

    def __validate_field(self, field_name: str):
        self.logger.debug(f"invalid parameter, {field_name} cannot be empty")
        raise InvalidParamException(
            f"Invalid input, analyzer result must contain {field_name}")
