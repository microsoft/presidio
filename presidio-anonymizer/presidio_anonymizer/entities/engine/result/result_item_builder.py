from presidio_anonymizer.entities.engine.result.anonymize_result_item import \
    AnonymizeResultItem
from presidio_anonymizer.entities.engine.result.decrypt_result_item import \
    DecryptResultItem
from presidio_anonymizer.entities.engine.result.engine_result_item import \
    EngineResultItem
from presidio_anonymizer.operators import OperatorType


class ResultItemBuilder:
    def __init__(self,
                 operator_type: OperatorType):
        self.__operator_type = operator_type
        self.__operator_name = ""
        self.__operated_on_text = ""
        self.__start = 0
        self.__end = 0
        self.__entity_type = ""

    def set_operator_name(self, operator_name: str) -> 'ResultItemBuilder':
        self.__operator_name = operator_name
        return self

    def set_entity_type(self, entity_type: str) -> 'ResultItemBuilder':
        self.__entity_type = entity_type
        return self

    def set_end(self, index_from_end: int) -> 'ResultItemBuilder':
        self.__end = index_from_end
        return self

    def manipulated_text(self, operated_on_text: str):
        self.__operated_on_text = operated_on_text
        return self

    def build(self) -> EngineResultItem:
        if self.__operator_type == OperatorType.Anonymize:
            return AnonymizeResultItem(self.__start, self.__end,
                                       self.__operated_on_text,
                                       self.__entity_type, self.__operator_name)

        return DecryptResultItem(self.__start, self.__end, self.__entity_type,
                                 self.__operated_on_text)
