import logging
from abc import ABC, abstractmethod
from collections import Counter
from collections.abc import Iterable
from typing import Dict, Iterator, List, Optional, Union

from pandas import DataFrame
from presidio_analyzer import (
    AnalyzerEngine,
    BatchAnalyzerEngine,
    DictAnalyzerResult,
    RecognizerResult,
)

from presidio_structured.config import StructuredAnalysis


class AnalysisBuilder(ABC):
    """Abstract base class for a configuration generator."""

    def __init__(self, analyzer: AnalyzerEngine = None) -> None:
        """Initialize the configuration generator."""
        self.analyzer = AnalyzerEngine() if analyzer is None else analyzer
        self.logger = logging.getLogger("presidio-structured")

    @abstractmethod
    def generate_analysis(
        self,
        data: Union[Dict, DataFrame],
        language: str = "en",
        score_threshold: Optional[float] = None,
    ) -> StructuredAnalysis:
        """
        Abstract method to generate a configuration from the given data.

        :param data: The input data. Can be a dictionary or DataFrame instance.
        :return: The generated configuration.
        """
        pass

    def _remove_low_scores(
        self,
        key_recognizer_result_map: Dict[str, RecognizerResult],
        score_threshold: float = None,
    ) -> List[RecognizerResult]:
        """
        Remove results for which the confidence is lower than the threshold.

        :param results: Dict of column names to RecognizerResult
        :param score_threshold: float value for minimum possible confidence
        :return: List[RecognizerResult]
        """
        if score_threshold is None:
            score_threshold = self.analyzer.default_score_threshold

        new_key_recognizer_result_map = {}
        for column, result in key_recognizer_result_map.items():
            if result.score >= score_threshold:
                new_key_recognizer_result_map[column] = result

        return new_key_recognizer_result_map


class JsonAnalysisBuilder(AnalysisBuilder):
    """Concrete configuration generator for JSON data."""

    def generate_analysis(
        self,
        data: Dict,
        language: str = "en",
        score_threshold: Optional[float] = None,
    ) -> StructuredAnalysis:
        """
        Generate a configuration from the given JSON data.

        :param data: The input JSON data.
        :return: The generated configuration.
        """
        self.logger.debug("Starting JSON BatchAnalyzer analysis")
        batch_analyzer = BatchAnalyzerEngine(analyzer_engine=self.analyzer)
        analyzer_results = batch_analyzer.analyze_dict(
            input_dict=data, language=language
        )

        key_recognizer_result_map = self._generate_analysis_from_results_json(
            analyzer_results
        )

        # Remove low score results
        key_recognizer_result_map = self._remove_low_scores(
            key_recognizer_result_map, score_threshold
        )

        key_entity_map = {
            key: result.entity_type for key, result in key_recognizer_result_map.items()
        }

        return StructuredAnalysis(entity_mapping=key_entity_map)

    def _generate_analysis_from_results_json(
        self, analyzer_results: Iterator[DictAnalyzerResult], prefix: str = ""
    ) -> Dict[str, RecognizerResult]:
        """
        Generate a configuration from the given analyzer results. \
             Always uses the first recognizer result if there are more than one.

        :param analyzer_results: The analyzer results.
        :param prefix: The prefix for the configuration keys.
        :return: The generated configuration.
        """
        key_recognizer_result_map = {}

        if not isinstance(analyzer_results, Iterable):
            self.logger.debug(
                "No analyzer results found, returning empty StructuredAnalysis"
            )
            return key_recognizer_result_map

        for result in analyzer_results:
            current_key = prefix + result.key

            if isinstance(result.value, dict):
                nested_mappings = self._generate_analysis_from_results_json(
                    result.recognizer_results, prefix=current_key + "."
                )
                key_recognizer_result_map.update(nested_mappings)
            first_recognizer_result = next(iter(result.recognizer_results), None)
            if first_recognizer_result is not None:
                self.logger.debug(
                    f"Found result with entity {first_recognizer_result.entity_type} \
                        in {current_key}"
                )
                key_recognizer_result_map[current_key] = first_recognizer_result
        return key_recognizer_result_map


class TabularAnalysisBuilder(AnalysisBuilder):
    """Placeholder class for generalizing tabular data analysis builders \
          (e.g. PySpark). Only implemented as PandasAnalysisBuilder for now."""

    pass


class PandasAnalysisBuilder(TabularAnalysisBuilder):
    """Concrete configuration generator for tabular data."""

    def generate_analysis(
        self,
        df: DataFrame,
        n: int = 100,
        language: str = "en",
        score_threshold: Optional[float] = None,
    ) -> StructuredAnalysis:
        """
        Generate a configuration from the given tabular data.

        :param df: The input tabular data (dataframe).
        :param n: The number of samples to be taken from the dataframe.
        :param language: The language to be used for analysis.
        :return: The generated configuration.
        """
        if n > len(df):
            self.logger.debug(
                f"Number of samples ({n}) is larger than the number of rows \
                    ({len(df)}), using all rows"
            )
            n = len(df)

        df = df.sample(n)

        key_recognizer_result_map = self._find_most_common_entity(df, language)

        # Remove low score results
        key_recognizer_result_map = self._remove_low_scores(
            key_recognizer_result_map, score_threshold
        )

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
        :param language: Language to be used in the analysis engine.
        :return: A dictionary mapping column names to the most common RecognizerResult.
        """
        key_recognizer_result_map = {}

        batch_analyzer = BatchAnalyzerEngine(analyzer_engine=self.analyzer)

        for column in df.columns:
            self.logger.debug(f"Finding most common PII entity for column {column}")
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
