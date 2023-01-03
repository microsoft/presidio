import csv
import pprint
import collections
from typing import List, Iterable, Optional, Union, Dict

from presidio_analyzer import AnalyzerEngine, BatchAnalyzerEngine, RecognizerResult, DictAnalyzerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import EngineResult

"""
Example implementing a CSV analyzer

This example shows how to use the Presidio Analyzer and Anonymizer
to detect and anonymize PII in a CSV file.
It uses the BatchAnalyzerEngine to analyze the CSV file, and the
BatchAnonymizerEngine to anonymize the requested columns.
Note that currently BatchAnonymizerEngine is not part of the anonymizer package,
and is defined in this and the batch_processing notebook.
https://github.com/microsoft/presidio/blob/main/docs/samples/python/batch_processing.ipynb

Content of csv file:
id,name,city,comments
1,John,New York,called him yesterday to confirm he requested to call back in 2 days
2,Jill,Los Angeles,accepted the offer license number AC432223
3,Jack,Chicago,need to call him at phone number 212-555-5555

"""


class CSVAnalyzer(BatchAnalyzerEngine):

    def analyze_csv(
        self,
        csv_full_path: str,
        language: str,
        keys_to_skip: Optional[List[str]] = None,
        **kwargs,
    ) -> Iterable[DictAnalyzerResult]:

        with open(csv_full_path, 'r') as csv_file:
            csv_list = list(csv.reader(csv_file))
            csv_dict = {header: list(map(str, values)) for header, *values in zip(*csv_list)}
            analyzer_results = self.analyze_dict(csv_dict, language, keys_to_skip)
            return list(analyzer_results)


class BatchAnonymizerEngine(AnonymizerEngine):
    """
    Class inheriting from the AnonymizerEngine and adding additional functionality 
    for anonymizing lists or dictionaries.
    """

    def anonymize_list(
        self,
        texts:List[Union[str, bool, int, float]], 
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
                res = self.anonymize(text=str(text), analyzer_results=recognizer_results, **kwargs)
                return_list.append(res.text)
            else:
                return_list.append(text)

        return return_list

    def anonymize_dict(self, analyzer_results: Iterable[DictAnalyzerResult], **kwargs) -> Dict[str, str]:

        """
        Anonymize values in a dictionary.

        :param analyzer_results: Iterator of `DictAnalyzerResult` 
        containing the output of the AnalyzerEngine.analyze_dict on the input text.
        :param kwargs: Additional kwargs for the `AnonymizerEngine.anonymize` method
        """

        return_dict = {}
        for result in analyzer_results:

            if isinstance(result.value, dict):
                resp = self.anonymize_dict(analyzer_results = result.recognizer_results, **kwargs)
                return_dict[result.key] = resp

            elif isinstance(result.value, str):
                resp = self.anonymize(text=result.value, analyzer_results=result.recognizer_results, **kwargs)
                return_dict[result.key] = resp.text

            elif isinstance(result.value, collections.abc.Iterable):
                anonymize_respones = self.anonymize_list(texts=result.value,
                                                         recognizer_results_list=result.recognizer_results, 
                                                         **kwargs)
                return_dict[result.key] = anonymize_respones 
            else:
                return_dict[result.key] = result.value
        return return_dict


if __name__ == "__main__":

    analyzer = CSVAnalyzer()
    analyzer_results = analyzer.analyze_csv('./csv_sample_data/sample_data.csv',
                                            language="en")
    pprint.pprint(analyzer_results)

    anonymizer = BatchAnonymizerEngine()
    anonymized_results = anonymizer.anonymize_dict(analyzer_results)
    pprint.pprint(anonymized_results)
