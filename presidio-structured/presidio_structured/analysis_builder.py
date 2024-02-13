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

NON_PII_ENTITY_TYPE = "NON_PII"

logger = logging.getLogger("presidio-structured")


class AnalysisBuilder(ABC):
    """Abstract base class for a configuration generator."""

    def __init__(
        self,
        analyzer: Optional[AnalyzerEngine] = None,
        analyzer_score_threshold: Optional[float] = None,
    ) -> None:
        """Initialize the configuration generator."""
        default_score_threshold = (
            analyzer_score_threshold if analyzer_score_threshold is not None else 0
        )
        self.analyzer = (
            AnalyzerEngine(default_score_threshold=default_score_threshold)
            if analyzer is None
            else analyzer
        )
        self.batch_analyzer = BatchAnalyzerEngine(analyzer_engine=self.analyzer)

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
        score_threshold: Optional[float] = None,
    ) -> Dict[str, RecognizerResult]:
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
    ) -> StructuredAnalysis:
        """
        Generate a configuration from the given JSON data.

        :param data: The input JSON data.
        :return: The generated configuration.
        """
        logger.debug("Starting JSON BatchAnalyzer analysis")
        analyzer_results = self.batch_analyzer.analyze_dict(
            input_dict=data, language=language
        )

        key_recognizer_result_map = self._generate_analysis_from_results_json(
            analyzer_results
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
            logger.debug(
                "No analyzer results found, returning empty StructuredAnalysis"
            )
            return key_recognizer_result_map

        for result in analyzer_results:
            current_key = prefix + result.key

            if isinstance(result.value, dict) and isinstance(
                result.recognizer_results, Iterator
            ):
                nested_mappings = self._generate_analysis_from_results_json(
                    result.recognizer_results, prefix=current_key + "."
                )
                key_recognizer_result_map.update(nested_mappings)
            first_recognizer_result = next(iter(result.recognizer_results), None)
            if isinstance(first_recognizer_result, RecognizerResult):
                logger.debug(
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
        n: Optional[int] = None,
        language: str = "en",
    ) -> StructuredAnalysis:
        """
        Generate a configuration from the given tabular data.

        :param df: The input tabular data (dataframe).
        :param n: The number of samples to be taken from the dataframe.
        :param language: The language to be used for analysis.
        :return: A StructuredAnalysis object containing the analysis results.
        """
        if not n:
            n = len(df)
        elif n > len(df):
            logger.debug(
                f"Number of samples ({n}) is larger than the number of rows \
                    ({len(df)}), using all rows"
            )
            n = len(df)

        df = df.sample(n, random_state=123)

        key_recognizer_result_map = self._generate_key_rec_results_map(df, language)

        key_entity_map = {
            key: result.entity_type
            for key, result in key_recognizer_result_map.items()
            if result.entity_type != NON_PII_ENTITY_TYPE
        }

        return StructuredAnalysis(entity_mapping=key_entity_map)

    def _generate_key_rec_results_map(
        self, df: DataFrame, language: str
    ) -> Dict[str, RecognizerResult]:
        """
        Find the most common entity in a dataframe column.

        If more than one entity is found in a cell, the first one is used.

        :param df: The dataframe where entities will be searched.
        :param language: Language to be used in the analysis engine.
        :return: A dictionary mapping column names to the most common RecognizerResult.
        """
        column_analyzer_results_map = self._batch_analyze_df(df, language)
        key_recognizer_result_map = {}
        for column, analyzer_result in column_analyzer_results_map.items():
            key_recognizer_result_map[column] = self._find_most_common_entity(
                analyzer_result
            )
        return key_recognizer_result_map

    def _batch_analyze_df(
        self, df: DataFrame, language: str
    ) -> Dict[str, List[List[RecognizerResult]]]:
        """
        Analyze each column in the dataframe for entities using the batch analyzer.

        :param df: The dataframe to be analyzed.
        :param language: The language configuration for the analyzer.
        :return: A dictionary mapping each column name to a \
            list of lists of RecognizerResults.
        """
        column_analyzer_results_map = {}
        for column in df.columns:
            logger.debug(f"Finding most common PII entity for column {column}")
            analyzer_results = self.batch_analyzer.analyze_iterator(
                [val for val in df[column]], language=language
            )
            column_analyzer_results_map[column] = analyzer_results

        return column_analyzer_results_map

    def _find_most_common_entity(
        self, analyzer_results: List[List[RecognizerResult]]
    ) -> RecognizerResult:
        """
        Find the most common entity in a list of analyzer results for \
            a dataframe column.

        It takes the most common entity type and calculates the confidence score based
        on the number of cells it appears in.

        :param analyzer_results: List of lists of RecognizerResults for each \
            cell in the column.
        :return: A RecognizerResult with the most common entity type and the \
            calculated confidence score.
        """

        if not any(analyzer_results):
            return RecognizerResult(
                entity_type=NON_PII_ENTITY_TYPE, start=0, end=1, score=1.0
            )

        # Flatten the list of lists while keeping track of the cell index
        flat_results = [
            (cell_idx, res)
            for cell_idx, cell_results in enumerate(analyzer_results)
            for res in cell_results
        ]

        # Count the occurrences of each entity type in different cells
        type_counter = Counter(res.entity_type for cell_idx, res in flat_results)

        # Find the most common entity type based on the number of cells it appears in
        most_common_type, _ = type_counter.most_common(1)[0]

        # The score is the ratio of the most common entity type's count to the total
        most_common_count = type_counter[most_common_type]
        score = most_common_count / len(analyzer_results)

        return RecognizerResult(
            entity_type=most_common_type, start=0, end=1, score=score
        )
