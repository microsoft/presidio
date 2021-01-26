import json
from typing import List, Optional, Dict, Union

from presidio_analyzer import (
    RecognizerRegistry,
    RecognizerResult,
    EntityRecognizer,
    PresidioLogger,
)
from presidio_analyzer.app_tracer import AppTracer
from presidio_analyzer.nlp_engine import NLP_ENGINES, NlpEngine

logger = PresidioLogger("presidio-analyzer")


class AnalyzerEngine:
    """
    Entry point for Presidio Analyzer.

    Orchestrating the detection of PII entities and all related logic.

    :param registry: instance of type RecognizerRegistry
    :param nlp_engine: instance of type NlpEngine
    (for example SpacyNlpEngine)
    :param app_tracer: instance of type AppTracer, used to trace the logic
    used during each request for interpretability reasons.
    :param enable_trace_pii: bool,
    defines whether PII values should be traced or not.
    :param default_score_threshold: Minimum confidence value
    for detected entities to be returned
    """

    def __init__(
        self,
        registry: RecognizerRegistry = None,
        nlp_engine: NlpEngine = None,
        app_tracer: AppTracer = None,
        enable_trace_pii: bool = False,
        default_score_threshold: float = 0,
        default_language: str = "en",
    ):

        if not nlp_engine:
            logger.info(
                "nlp_engine not provided. Creating new " "SpacyNlpEngine instance"
            )
            nlp_engine = NLP_ENGINES["spacy"]()
        if not registry:
            logger.info(
                "Recognizer registry not provided. "
                "Creating default RecognizerRegistry instance"
            )
            registry = RecognizerRegistry()
        if not app_tracer:
            app_tracer = AppTracer()
        self.app_tracer = app_tracer

        self.default_language = default_language

        self.nlp_engine = nlp_engine
        self.registry = registry

        # load all recognizers
        if not registry.recognizers:
            registry.load_predefined_recognizers()

        self.enable_trace_pii = enable_trace_pii
        self.default_score_threshold = default_score_threshold

    def get_recognizers(self, language: Optional[str] = None) -> List[EntityRecognizer]:
        """
        Return a list of PII recognizers currently loaded.

        :param language: Return the recognizers supporting a given language.
        :return: List of [Recognizer] as a RecognizersAllResponse
        """
        if not language:
            language = self.default_language
        logger.info(f"Fetching all recognizers for language {language}")
        recognizers = self.registry.get_recognizers(language=language, all_fields=True)
        return recognizers

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
        trace: Optional[bool] = False,
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
        :param trace: Should tracing of the response occur or not
        :return: an array of the found entities in the text
        """
        all_fields = not entities

        recognizers = self.registry.get_recognizers(
            language=language, entities=entities, all_fields=all_fields
        )

        if all_fields:
            # Since all_fields=True, list all entities by iterating
            # over all recognizers
            entities = self.get_supported_entities(language=language)

        # run the nlp pipeline over the given text, store the results in
        # a NlpArtifacts instance
        nlp_artifacts = self.nlp_engine.process_text(text, language)

        if self.enable_trace_pii and trace:
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

        if trace:
            self.app_tracer.trace(
                correlation_id, json.dumps([result.to_json() for result in results])
            )

        # Remove duplicates or low score results
        results = EntityRecognizer.remove_duplicates(results)
        results = self.__remove_low_scores(results, score_threshold)

        return results

    def analyze_batch(
        self,
        batch_dict: Dict[str, List[str]],
        language: str = "en",
        keys_to_skip: Optional[List[str]] = None,
        entities: Optional[List[str]] = None,
        score_threshold: Optional[float] = None,
        **kwargs,  # noqa ANN003
    ) -> Union[List[RecognizerResult], Dict[str, List[List[RecognizerResult]]]]:
        """
        Run analysis on a dictionary containing a list of values.

        Could be used for:
        a. Identifying PII in specific keys on a json object
        b. Identifying PII on a list of values, and not one-by-one.
        :param batch_dict: A dictionary containing one or more keys with corresponding
        lists of strings containing values to analyze,
        or a single string to be processed.
        For example, a table can be represented as a dictionary of columns,
        where the key is the column name
        and the value is the list of values for this column. If using Pandas,
        transform the data frame to a dict using df.to_dict(orient="list")
        :param language: The language of the text
        :param keys_to_skip: List of keys to skip analysis for.
        In such case a list of entities should be provided.
        :param entities: List of PII entities that should be looked for in the text.
        If entities=None and all_fields=True then all entities are looked for.
        :param score_threshold: value to ignore results with score lower than threshold
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
                    language=language,
                    entities=entities,
                    score_threshold=score_threshold,
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
