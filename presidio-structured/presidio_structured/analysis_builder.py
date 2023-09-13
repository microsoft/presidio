from abc import ABC, abstractmethod
from collections import Counter
from collections.abc import Iterable
from typing import Any, Dict, Iterator, Union

from pandas import DataFrame
from presidio_analyzer import (
    AnalyzerEngine,
    BatchAnalyzerEngine,
    DictAnalyzerResult,
    RecognizerResult,
)

from presidio_structured.config import StructuredAnalysis


class AnalysisBuilder(ABC):
    """
    Abstract base class for a configuration generator.
    """

    def __init__(self):
        """Initialize the configuration generator."""
        self.analyzer = AnalyzerEngine()

    @abstractmethod
    def generate_analysis(self, data: Union[Dict, DataFrame]) -> StructuredAnalysis:
        """
        Abstract method to generate a configuration from the given data.

        :param data: The input data. Can be a dictionary or DataFrame instance.
        :type data: Union[Dict, DataFrame]
        :return: The generated configuration.
        :rtype StructuredAnalysis:
        """
        pass


class JsonAnalysisBuilder(AnalysisBuilder):
    """Concrete configuration generator for JSON data."""

    def generate_analysis(self, data: Dict) -> StructuredAnalysis:
        """
        Generate a configuration from the given JSON data.

        :param data: The input JSON data.
        :type data: Dict
        :return: The generated configuration.
        :rtype StructuredAnalysis:
        """
        batch_analyzer = BatchAnalyzerEngine(analyzer_engine=self.analyzer)
        analyzer_results = batch_analyzer.analyze_dict(input_dict=data, language="en")
        return self._generate_analysis_from_results_json(analyzer_results)

    def _generate_analysis_from_results_json(
        self, analyzer_results: Iterator[DictAnalyzerResult], prefix: str = ""
    ) -> StructuredAnalysis:
        """
        Generate a configuration from the given analyzer results.

        :param analyzer_results: The analyzer results.
        :type analyzer_results: Iterator[DictAnalyzerResult]
        :param prefix: The prefix for the configuration keys.
        :type prefix: str
        :return: The generated configuration.
        :rtype StructuredAnalysis:
        """
        mappings = {}

        if not isinstance(analyzer_results, Iterable):
            return mappings

        for result in analyzer_results:
            current_key = prefix + result.key

            if isinstance(result.value, dict):
                nested_mappings = self._generate_analysis_from_results_json(
                    result.recognizer_results, prefix=current_key + "."
                )
                mappings.update(nested_mappings.entity_mapping)

            if sum(1 for _ in result.recognizer_results) > 0:
                for recognizer_result in result.recognizer_results:
                    mappings[current_key] = recognizer_result.entity_type
        return StructuredAnalysis(entity_mapping=mappings)


class TabularAnalysisBuilder(AnalysisBuilder):
    """Concrete configuration generator for tabular data."""

    def generate_analysis(
        self, df: DataFrame, n: int = 100, language: str = "en"
    ) -> StructuredAnalysis:
        """
        Generate a configuration from the given tabular data.

        :param df: The input tabular data (dataframe).
        :type df: DataFrame
        :param n: The number of samples to be taken from the dataframe.
        :type n: int
        :param language: The language to be used for analysis.
        :type language: str
        :return: The generated configuration.
        :rtype StructuredAnalysis:
        """
        if n > len(df):
            n = len(df)

        df = df.sample(n)

        key_recognizer_result_map = self._find_most_common_entity(df, language)

        key_entity_map = {
            key: result.entity_type
            for key, result in key_recognizer_result_map.items()
            if result.entity_type != "NON_PII"
        }

        return StructuredAnalysis(entity_mapping=key_entity_map)

    def _find_most_common_entity(
        self, df: DataFrame, language: str
    ) -> Dict[str, RecognizerResult]:
        """
        Find the most common entity in a dataframe column.

        :param df: The dataframe where entities will be searched.
        :type df: DataFrame
        :param language: Language to be used in the analysis engine.
        :type language: str
        :return: A dictionary mapping column names to the most common RecognizerResult.
        :rtype: Dict[str, RecognizerResult]
        """
        key_recognizer_result_map = {}

        for column in df.columns:
            batch_analyzer = BatchAnalyzerEngine(analyzer_engine=self.analyzer)
            analyzer_results = batch_analyzer.analyze_iterator(
                [val for val in df[column]], language=language
            )

            if all(len(res) == 0 for res in analyzer_results):
                key_recognizer_result_map[column] = RecognizerResult(
                    entity_type="NON_PII", start=0, end=1, score=1.0
                )
                continue
            # Grabbing most common type
            types_list = [
                res[0].entity_type for res in analyzer_results if len(res) > 0
            ]
            type_counter = Counter(types_list)
            most_common_type = type_counter.most_common(1)[0][0]
            # Grabbing the average confidence score for the most common type.
            scores = [
                res[0].score
                for res in analyzer_results
                if len(res) > 0 and res[0].entity_type == most_common_type
            ]
            average_score = sum(scores) / len(scores) if scores else 0.0
            key_recognizer_result_map[column] = RecognizerResult(
                most_common_type, 0, 1, average_score
            )
        return key_recognizer_result_map
