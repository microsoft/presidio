class OperatorResult:
    """A class to hold data for engines results either anonymize or deanonymize."""

    def __init__(self, text: str, operator_name: str, start: int, end: int,
                 entity_type: str):
        self.start = start
        self.end = end
        self.entity_type = entity_type
        self.text = text
        self.operator = operator_name

    def __eq__(self, other: 'OperatorResult') -> bool:
        """
        Verify two OperatorResults are equal.

        :param other: OperatorResult
        :return: bool
        """
        return (self.start == other.start
                and self.end == other.end
                and self.entity_type == other.entity_type
                and self.operator == other.operator
                and self.text == other.text)
