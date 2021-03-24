from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.engine.result import AnonymizedEntity
from presidio_anonymizer.entities.engine.result import DecryptedEntity
from presidio_anonymizer.entities.engine.result import EngineResultItem
from presidio_anonymizer.operators import OperatorType


class ResultItemBuilder:
    """Build a result item for the engine result according to the operator type."""

    def __init__(self,
                 operator_type: OperatorType):
        """

        :param operator_type: the operator type anonymize/decrypt
        """
        self.__operator_type = operator_type
        self.__operator_name = ""
        self.__operated_on_text = ""
        self.__start = 0
        self.__end = 0
        self.__entity_type = ""

    def set_operator_name(self, operator_name: str) -> 'ResultItemBuilder':
        """Set operator name of the result item."""
        self.__operator_name = operator_name
        return self

    def set_entity_type(self, entity_type: str) -> 'ResultItemBuilder':
        """Set entity type of the result item."""
        self.__entity_type = entity_type
        return self

    def set_end(self, index_from_end: int) -> 'ResultItemBuilder':
        """Set end index of the text result item."""
        self.__end = index_from_end
        return self

    def set_operated_on_text(self, operated_on_text: str):
        """Set the text we operated over."""
        self.__operated_on_text = operated_on_text
        return self

    def build(self) -> EngineResultItem:
        """Create a EngineResultItem either for Anonymize or Decrypt."""
        if self.__operator_type == OperatorType.Anonymize:
            return AnonymizedEntity(self.__start, self.__end,
                                    self.__operated_on_text,
                                    self.__entity_type, self.__operator_name)

        if self.__operator_type == OperatorType.Decrypt:
            return DecryptedEntity(self.__start, self.__end, self.__entity_type,
                                   self.__operated_on_text)

        raise InvalidParamException(f"Invalid operator type {self.__operator_type}")
