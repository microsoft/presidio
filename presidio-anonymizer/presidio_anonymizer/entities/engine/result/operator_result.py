class OperatorResult:
    """An abstract class to hold mutual data for engines results."""

    def __init__(self, text: str, operator_name: str, start: int, end: int,
                 entity_type: str):
        self.start = start
        self.end = end
        self.entity_type = entity_type
        self.text = text
        self.operator_name = operator_name

    def __eq__(self, other: 'OperatorResult') -> bool:
        """
        Verify two DecryptedEntity are equal.

        :param other: DecryptedEntity
        :return: bool
        """
        return (self.start == other.start
                and self.end == other.end
                and self.entity_type == other.entity_type
                and self.operator_name == other.operator_name
                and self.text == other.text)

    def get_text(self):
        """
        Get the text after we performed the operator over it.

        :return: the text we operated over and this decrypt result represent.
        """
        return self.text
