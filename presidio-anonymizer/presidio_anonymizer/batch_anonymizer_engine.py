from typing import List, Dict, Union, Iterable
import collections

from presidio_anonymizer.entities import DictRecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import EngineResult, RecognizerResult


class BatchAnonymizerEngine(AnonymizerEngine):
    """
    BatchAnonymizerEngine class.

    Class inheriting from the AnonymizerEngine, with additional anonymize functionality
    for lists and dictionaries.
    """

    def anonymize_list(
        self,
        texts: List[Union[str, bool, int, float]],
        recognizer_results_list: List[List[RecognizerResult]],
        **kwargs
    ) -> List[EngineResult]:
        """
        Anonymize a list of strings.

        :param texts: List containing the texts to be anonymized (original texts)
        :param recognizer_results_list: A list of lists of RecognizerResult,
        the output of the AnalyzerEngine on each text in the list.
        :param kwargs: Additional kwargs for the `AnonymizerEngine.anonymize` method
        """
        return_list = []
        if not recognizer_results_list:
            recognizer_results_list = [[] for _ in range(len(texts))]
        for text, recognizer_results in zip(texts, recognizer_results_list):
            if type(text) in (str, bool, int, float):
                res = self.anonymize(
                    text=str(text), analyzer_results=recognizer_results, **kwargs
                )
                return_list.append(res.text)
            else:
                return_list.append(text)

        return return_list

    def anonymize_dict(
        self, analyzer_results: Iterable[DictRecognizerResult], **kwargs
    ) -> Dict[str, str]:
        """
        Anonymize values in a dictionary.

        :param analyzer_results: Iterator of `DictRecognizerResult`
        containing the output of the AnalyzerEngine.analyze_dict on the input text.
        :param kwargs: Additional kwargs for the `AnonymizerEngine.anonymize` method
        """

        return_dict = {}
        for result in analyzer_results:
            if isinstance(result.value, dict):
                resp = self.anonymize_dict(
                    analyzer_results=result.recognizer_results, **kwargs
                )
                return_dict[result.key] = resp

            elif isinstance(result.value, str):
                resp = self.anonymize(
                    text=result.value,
                    analyzer_results=result.recognizer_results,
                    **kwargs
                )
                return_dict[result.key] = resp.text

            elif isinstance(result.value, collections.abc.Iterable):
                anonymize_response = self.anonymize_list(
                    texts=result.value,
                    recognizer_results_list=result.recognizer_results,
                    **kwargs
                )
                return_dict[result.key] = anonymize_response
            else:
                return_dict[result.key] = result.value
        return return_dict
