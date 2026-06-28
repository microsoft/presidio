import collections
from typing import Any, Dict, Iterable, List, Optional, Union

from presidio_anonymizer.deanonymize_engine import DeanonymizeEngine
from presidio_anonymizer.entities import (
    DictRecognizerResult,
    OperatorConfig,
    OperatorResult,
)


class BatchDeanonymizeEngine:
    """
    BatchDeanonymizeEngine class.

    A class that provides functionality to deanonymize in batches.
    :param deanonymize_engine: An instance of the DeanonymizeEngine class.
    """

    def __init__(self, deanonymize_engine: Optional[DeanonymizeEngine] = None):
        self.deanonymize_engine = deanonymize_engine or DeanonymizeEngine()

    def deanonymize_list(
        self,
        texts: List[Optional[Union[str, bool, int, float]]],
        entities_list: List[List[OperatorResult]],
        operators: Dict[str, OperatorConfig],
        **kwargs,
    ) -> List[Union[str, Any]]:
        """
        Deanonymize a list of strings.

        :param texts: List containing the texts to be deanonymized.
            Items with a `type` not in `(str, bool, int, float)` will be left
            unchanged.
        :param entities_list: A list of lists of OperatorResult, the output of
            DeanonymizeEngine.deanonymize on each text in the list.
        :param operators: Operators to define the deanonymization type.
        :param kwargs: Additional kwargs for the `DeanonymizeEngine.deanonymize` method
        """
        return_list = []
        if not entities_list:
            entities_list = [[] for _ in range(len(texts))]
        for text, entities in zip(texts, entities_list):
            if type(text) in (str, bool, int, float):
                res = self.deanonymize_engine.deanonymize(
                    text=str(text), entities=entities, operators=operators, **kwargs
                )
                return_list.append(res.text)
            else:
                return_list.append(text)

        return return_list

    def deanonymize_dict(
        self,
        analyzer_results: Iterable[DictRecognizerResult],
        operators: Dict[str, OperatorConfig],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Deanonymize values in a dictionary.

        :param analyzer_results: Iterator of `DictRecognizerResult`
            containing the output of the AnalyzerEngine.analyze_dict on the input text.
        :param operators: Operators to define the deanonymization type.
        :param kwargs: Additional kwargs for the `DeanonymizeEngine.deanonymize` method
        """

        return_dict = {}
        for result in analyzer_results:
            if isinstance(result.value, dict):
                resp = self.deanonymize_dict(
                    analyzer_results=result.recognizer_results,
                    operators=operators,
                    **kwargs,
                )
                return_dict[result.key] = resp

            elif isinstance(result.value, str):
                resp = self.deanonymize_engine.deanonymize(
                    text=result.value,
                    entities=result.recognizer_results,
                    operators=operators,
                    **kwargs,
                )
                return_dict[result.key] = resp.text

            elif isinstance(result.value, collections.abc.Iterable):
                deanonymize_response = self.deanonymize_list(
                    texts=result.value,
                    entities_list=result.recognizer_results,
                    operators=operators,
                    **kwargs,
                )
                return_dict[result.key] = deanonymize_response
            else:
                return_dict[result.key] = result.value
        return return_dict
