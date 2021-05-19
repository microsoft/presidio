import collections
import json
from typing import List, Optional, Dict, Union, Iterator, Iterable
import logging

from presidio_analyzer import (
    RecognizerRegistry,
    RecognizerResult,
    EntityRecognizer,
    DictAnalyzerResult,
)
from presidio_analyzer.app_tracer import AppTracer
from presidio_analyzer.nlp_engine import NlpEngine, NlpEngineProvider

logger = logging.getLogger("presidio-analyzer")


class AnalyzerEngine:
    """
    Entry point for Presidio Analyzer.

    Orchestrating the detection of PII entities and all related logic.

    :param registry: instance of type RecognizerRegistry
    :param nlp_engine: instance of type NlpEngine
    (for example SpacyNlpEngine)
    :param app_tracer: instance of type AppTracer, used to trace the logic
    used during each request for interpretability reasons.
    :param log_decision_process: bool,
    defines whether the decision process within the analyzer should be logged or not.
    :param default_score_threshold: Minimum confidence value
    for detected entities to be returned
    :param supported_languages: List of possible languages this engine could be run on.
    Used for loading the right NLP models and recognizers for these languages.
    """

    def __init__(
        self,
        registry: RecognizerRegistry = None,
        nlp_engine: NlpEngine = None,
        app_tracer: AppTracer = None,
        log_decision_process: bool = False,
        default_score_threshold: float = 0,
        supported_languages: List[str] = None,
    ):
        if not supported_languages:
            supported_languages = ["en"]

        if not nlp_engine:
            logger.info("nlp_engine not provided, creating default.")
            provider = NlpEngineProvider()
            nlp_engine = provider.create_engine()

        if not registry:
            logger.info("registry not provided, creating default.")
            registry = RecognizerRegistry()
        if not app_tracer:
            app_tracer = AppTracer()
        self.app_tracer = app_tracer

        self.supported_languages = supported_languages

        self.nlp_engine = nlp_engine
        self.registry = registry

        # load all recognizers
        if not registry.recognizers:
            registry.load_predefined_recognizers(
                nlp_engine=self.nlp_engine, languages=self.supported_languages
            )

        self.log_decision_process = log_decision_process
        self.default_score_threshold = default_score_threshold

    def get_recognizers(self, language: Optional[str] = None) -> List[EntityRecognizer]:
        """
        Return a list of PII recognizers currently loaded.

        :param language: Return the recognizers supporting a given language.
        :return: List of [Recognizer] as a RecognizersAllResponse
        """
        if not language:
            languages = self.supported_languages
        else:
            languages = [language]

        recognizers = []
        for language in languages:
            logger.info(f"Fetching all recognizers for language {language}")
            recognizers.extend(
                self.registry.get_recognizers(language=language, all_fields=True)
            )

        return list(set(recognizers))

    def get_supported_entities(self, language: Optional[str] = None) -> List[str]:
        """
        Return a list of the entities that can be detected.

        :param language: Return only entities supported in a specific language.
        :return: List of entity names
        """
        recognizers = self.get_recognizers(language=language)
        supported_entities = []
        for recognizer in recognizers:
            supported_entities.extend(recognizer.get_supported_entities())

        return list(set(supported_entities))

    def analyze(
        self,
        text: str,
        language: str,
        entities: Optional[List[str]] = None,
        correlation_id: Optional[str] = None,
        score_threshold: Optional[float] = None,
        return_decision_process: Optional[bool] = False,
        ad_hoc_recognizers: Optional[List[EntityRecognizer]] = None,
    ) -> List[RecognizerResult]:
        """
        Find PII entities in text using different PII recognizers for a given language.

        :param text: the text to analyze
        :param language: the language of the text
        :param entities: List of PII entities that should be looked for in the text.
        If entities=None then all entities are looked for.
        :param correlation_id: cross call ID for this request
        :param score_threshold: A minimum value for which
        to return an identified entity
        :param return_decision_process: Whether the analysis decision process steps
        returned in the response.
        :param ad_hoc_recognizers: List of recognizers which will be used only
        for this specific request.
        :return: an array of the found entities in the text

        :example:

        >>> from presidio_analyzer import AnalyzerEngine

        >>> # Set up the engine, loads the NLP module (spaCy model by default)
        >>> # and other PII recognizers
        >>> analyzer = AnalyzerEngine()

        >>> # Call analyzer to get results
        >>> results = analyzer.analyze(text='My phone number is 212-555-5555', entities=['PHONE_NUMBER'], language='en') # noqa D501
        >>> print(results)
        [type: PHONE_NUMBER, start: 19, end: 31, score: 0.85]
        """
        all_fields = not entities

        recognizers = self.registry.get_recognizers(
            language=language,
            entities=entities,
            all_fields=all_fields,
            ad_hoc_recognizers=ad_hoc_recognizers,
        )

        if all_fields:
            # Since all_fields=True, list all entities by iterating
            # over all recognizers
            entities = self.get_supported_entities(language=language)

        # run the nlp pipeline over the given text, store the results in
        # a NlpArtifacts instance
        nlp_artifacts = self.nlp_engine.process_text(text, language)

        if self.log_decision_process:
            self.app_tracer.trace(
                correlation_id, "nlp artifacts:" + nlp_artifacts.to_json()
            )

        results = []
        for recognizer in recognizers:
            # Lazy loading of the relevant recognizers
            if not recognizer.is_loaded:
                recognizer.load()
                recognizer.is_loaded = True

            # analyze using the current recognizer and append the results
            current_results = recognizer.analyze(
                text=text, entities=entities, nlp_artifacts=nlp_artifacts
            )
            if current_results:
                results.extend(current_results)

        if self.log_decision_process:
            self.app_tracer.trace(
                correlation_id,
                json.dumps([str(result.to_dict()) for result in results]),
            )

        # Remove duplicates or low score results
        results = EntityRecognizer.remove_duplicates(results)
        results = self.__remove_low_scores(results, score_threshold)

        if not return_decision_process:
            results = self.__remove_decision_process(results)

        return results

    def analyze_list(
        self, list_of_texts: Iterable[str], **kwargs
    ) -> List[List[RecognizerResult]]:
        """
        Run analysis on a list of strings.

        :param list_of_texts: Input data
        :param kwargs: additional parameters to the analyze method
        :return: List of List[RecognizerResult]
        """
        list_results = []
        for text in list_of_texts:
            results = self.analyze(text=text, **kwargs) if isinstance(text, str) else []
            list_results.append(results)

        return list_results

    def analyze_dict(
        self, input_dict: Dict[str, Union[str, Iterable[str]]], **kwargs
    ) -> Iterator[DictAnalyzerResult]:
        """
        Run analysis on a full dictionary.

        :param input_dict: Input data
        :param kwargs: Additional parameters for the analyze method.
        :return: Iterator with analyzer results per value
        """

        for key, value in input_dict.items():
            if not value:
                results = []
            else:
                if isinstance(value, str):
                    results: List[RecognizerResult] = self.analyze(text=value, **kwargs)
                elif isinstance(value, collections.Iterable):
                    results: List[List[RecognizerResult]] = self.analyze_list(
                        list_of_texts=value, key=key, **kwargs
                    )
                else:
                    results = []

            yield DictAnalyzerResult(key=key, value=value, recognizer_results=results)

    def analyze_batch(
        self,
        batch_dict: Dict[str, object],
        keys_to_skip: Optional[List[str]] = None,
        **kwargs,  # noqa ANN003
    ) -> Union[List[RecognizerResult], DictAnalyzerResult]:
        """
        Run analysis on a dictionary containing a list of values.

        Could be used for:
        a. Identifying PII in a table represented as a
        dictionary of keys ad list of values per key.
        a. Identifying PII in specific keys on a json object.
        b. Identifying PII on a list of values.
        :param data: Either a string, a dictionary of type Dict[str,object],
        or a list of strings.

        For example, a table can be represented as a dictionary of columns,
        where the key is the column name
        and the value is the list of values for this column. If using Pandas,
        transform the data frame to a dict using df.to_dict(orient="list")
        :para batch_dict: Input data
        :param keys_to_skip: List of keys to skip analysis for.
        In such case a list of entities should be provided.
        :param kwargs: additional parameters for the analyze function
        :return: A dictionary containing the original keys, and a list of results
        (list of list of RecognizerResult) from the various recognizers.
        """

        if not batch_dict:
            raise ValueError(
                "Input not provided. batch should be a dictionary "
                "containing one or more keys with corresponding "
                "lists of strings containing values to analyze"
            )
        if not isinstance(batch_dict, dict):
            raise ValueError(
                "Input parameter batch should be a dict containing "
                "a list of strings per key. "
                "For the analysis of one string, run the analyze function)"
            )

        response = {}
        for key, list_of_texts in batch_dict.items():
            if keys_to_skip and key in keys_to_skip:
                continue
            per_text_responses = []
            for text in list_of_texts:
                analyzer_response = self.analyze(
                    text=text,
                    **kwargs,
                )
                per_text_responses.append(analyzer_response)
            response[key] = per_text_responses
        return response

    def __remove_low_scores(
        self, results: List[RecognizerResult], score_threshold: float = None
    ) -> List[RecognizerResult]:
        """
        Remove results for which the confidence is lower than the threshold.

        :param results: List of RecognizerResult
        :param score_threshold: float value for minimum possible confidence
        :return: List[RecognizerResult]
        """
        if score_threshold is None:
            score_threshold = self.default_score_threshold

        new_results = [result for result in results if result.score >= score_threshold]
        return new_results

    @staticmethod
    def __remove_decision_process(
        results: List[RecognizerResult],
    ) -> List[RecognizerResult]:
        """Remove decision process / analysis explanation from response."""

        for result in results:
            result.analysis_explanation = None

        return results
