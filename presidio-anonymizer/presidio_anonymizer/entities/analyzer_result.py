"""
AnalyzerResult is the exact copy of the recognizer result.

Represents the findings of detected entity.
"""
from presidio_anonymizer.entities.invalid_exception import InvalidParamException


class AnalyzerResult(object):
    """
    AnalyzerResult is a duplication of the recognizer result.

    Validate and compare an recognizer result object.
    """

    def __init__(self,
                 entity_type: str,
                 score: float,
                 start: int,
                 end: int):
        """
         Analyzer Result represents the detected entity of the analyzer in the text.

        :param entity_type: type of the entity (PHONE_NUMBER etc.)
        :param score: the score given by the recognizer
        :param start: start index in the text
        :param end: end index in the text
        """
        self.score = score
        self.entity_type = entity_type
        self.start = start
        self.end = end

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
        return self.equal_indices(
            other) and self.entity_type.__eq__(
            other.entity_type) and self.score is other.score

    def __hash__(self):
        """
        Hash the result data by using all class fields.

        :return: int
        """
        return hash(
            f"{str(self.start)} {str(self.end)} {str(self.score)} {self.entity_type}")

    def same_or_contained(self, other):
        """
        Check is two analyzer results are contained or the same.

        :param other: AnalyzerResult
        :return:
        """
        return other.contains(self) or (
                self.equal_indices(other) and self.score < other.score)

    @classmethod
    def validate_and_create(cls, content):
        """
        Validate and create analyzer result from user input and json.

        :param content: json with analyzer result. See example in payload.json
        :return: AnalyzerResult
        """
        cls.__validate_fields(content)
        return cls(content.get("entity_type"), content.get("score"),
                   content.get("start"),
                   content.get("end"))

    @classmethod
    def __validate_fields(cls, content):
        for field in ["start", "end", "score", "entity_type"]:
            if content.get(field) is None:
                raise InvalidParamException(
                    f"Invalid input, analyzer result must contain {field}")
