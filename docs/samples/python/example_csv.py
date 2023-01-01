import csv
import pprint
from typing import List, Iterable, Optional

from presidio_analyzer import BatchAnalyzerEngine, DictAnalyzerResult
from presidio_anonymizer import BatchAnonymizerEngine

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


if __name__ == "__main__":

    analyzer = CSVAnalyzer()
    analyzer_results = analyzer.analyze_csv('docs/samples/python/csv_sample_data/sample_data.csv',
                                            language="en")
    pprint.pprint(analyzer_results)

    anonymizer = BatchAnonymizerEngine()
    anonymized_results = anonymizer.anonymize_dict(analyzer_results)
    pprint.pprint(anonymized_results)
