from typing import Any, Dict, Union

from pandas import DataFrame
from presidio_anonymizer.entities import OperatorConfig

from presidio_structured.config import StructuredAnalysis
from presidio_structured.data.data_processors import (
    DataProcessorBase,
    PandasDataProcessor,
)

DEFAULT = "replace"


class StructuredEngine:
    """
    Class to implement methods for anonymizing tabular data.
    """

    def __init__(self, data_processor: DataProcessorBase = None) -> None:
        """
        Initialize the class with a data processor.

        :param data_processor: Instance of DataProcessorBase.
        """
        if data_processor is None:
            data_processor = PandasDataProcessor()
        self.data_processor = data_processor

    def anonymize(
        self,
        data: Union[Dict, DataFrame],
        structured_analysis: StructuredAnalysis,
        operators: Dict[str, OperatorConfig] = None,
    ) -> Union[Dict, DataFrame]:
        """
        Anonymize the given data using the given configuration.

        :param data: input data as dictionary or pandas DataFrame.
        :param structured_analysis: structured analysis configuration.
        :param operators: a dictionary of operator configurations, optional.
        :return: Anonymized dictionary or DataFrame.
        """
        operators = self.__check_or_add_default_operator(operators)

        return self.data_processor.operate(data, structured_analysis, operators)

    @staticmethod
    def __check_or_add_default_operator(
        operators: Dict[str, OperatorConfig]
    ) -> Dict[str, OperatorConfig]:
        """
        Check if the provided operators dictionary has a default operator.
        If not, add a default operator.

        :param operators: dictionary of operator configurations.
        :return: operators dictionary with the default operator added if it was not initially present.
        """
        default_operator = OperatorConfig(DEFAULT)
        if not operators:
            return {"DEFAULT": default_operator}
        if not operators.get("DEFAULT"):
            operators["DEFAULT"] = default_operator
        return operators
