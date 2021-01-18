"""
AnalyzerResult is the exact copy of the recognizer result.

Represents the findings of detected entity.
"""
from presidio_anonymizer.domain.invalid_exception import InvalidJsonException


class AnalyzerResult(object):
    def __init__(self,
                 entity_type: str,
                 score: float,
                 start: int,
                 end: int):
        """
       Analyzer Result represents the findings of the detected entity
       of the analyzer in the text.
       :param entity_type: the type of the entity
       :param start: the start location of the detected entity
       :param end: the end location of the detected entity
       :param score: the score of the detection
       """
        self.score = score
        self.entity_type = entity_type
        self.start = start
        self.end = end

    def contains(self, other):
        return self.start <= other.start and self.end >= other.end

    def equal_indices(self, other):
        return self.start == other.start and self.end == other.end

    def __gt__(self, other):
        if self.start == other.start:
            return self.end > other.end
        return self.start > other.start

    def __eq__(self, other):
        return self.equal_indices(other) and \
               self.entity_type == other.entity_type and self.score == other.score

    def __hash__(self):
        return hash(str(self.start) + " " + str(self.end) + " " + str(
            self.score) + " " + self.entity_type)

    @classmethod
    def validate_and_convert(cls, content):
        cls.__validate_fields(content)
        return cls(content.get("entity_type"), content.get("score"),
                   content.get("start"),
                   content.get("end"))

    @classmethod
    def __validate_fields(cls, content):
        for field in ["start", "end", "score", "entity_type"]:
            if content.get(field) is None:
                raise InvalidJsonException(
                    f"Invalid json, analyzer result must contain {field}")
