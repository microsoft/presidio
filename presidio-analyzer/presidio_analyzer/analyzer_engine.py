import json
from typing import List, Dict, Optional, Union

from presidio_analyzer import (
    PresidioLogger,
    RecognizerRegistry,
    RecognizerResult,
    EntityRecognizer,
)
from presidio_analyzer.app_tracer import AppTracer
from presidio_analyzer.nlp_engine import NLP_ENGINES


logger = PresidioLogger("presidio")


class AnalyzerEngine:
    def __init__(
        self,
        registry=None,
        nlp_engine=None,
        app_tracer=None,
        enable_trace_pii=False,
        default_score_threshold=None,
        default_language="en",
    ):
        """
        AnalyzerEngine class: Orchestrating the detection of PII entities
        and all related logic
        :param registry: instance of type RecognizerRegistry
        :param nlp_engine: instance of type NlpEngine
        (for example SpacyNlpEngine)
        :param app_tracer: instance of type AppTracer,
        used to trace the logic used during each request
        :param enable_trace_pii: bool,
        defines whether PII values should be traced or not.
        :param default_score_threshold: Minimum confidence value
        for detected entities to be returned
        """
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

        self.default_language = default_language

        # load nlp module
        self.nlp_engine = nlp_engine
        # prepare registry
        self.registry = registry
        # load all recognizers
        if not registry.recognizers:
            registry.load_predefined_recognizers()

        self.app_tracer = app_tracer
        self.enable_trace_pii = enable_trace_pii

        self.default_score_threshold = (
            default_score_threshold if default_score_threshold else 0.0
        )

    def get_recognizers(self, language: Optional[str] = None) -> List[EntityRecognizer]:
        """
        :return: List of [Recognizer] as a RecognizersAllResponse
        """
        if not language:
            language = self.default_language
        logger.info(f"Fetching all recognizers Recognizers for language {language}")
        recognizers = self.registry.get_recognizers(language=language, all_fields=True)
        return recognizers

    def analyze_batch(
        self,
        batch: Dict[str, List[str]],
        language: str,
        all_fields: bool,
        entities: Optional[List[str]] = None,
        score_threshold: Optional[float] = None,
        **kwargs,
    ) -> Union[List[RecognizerResult], Dict[str, List[List[RecognizerResult]]]]:
        """
        Processes a dictionary containing a list of values.
        Could be used for:
        a. Identifying PII in specific keys on a json object
        b. Identifying PII on a list of values, and not one-by-one.
        :param batch: A dictionary containing one or more keys with corresponding
        lists of strings containing values to analyze,
        or a single string to be processed.
        :param language: The language of the text
        :param all_fields: True if the analyzer should look for all types of PII,
        False if use only a subset of the recognizers.
        In such case a list of entities should be provided.
        :param entities: List of PII entities that should be looked for in the text.
        If entities=None and all_fields=True then all entities are looked for.
        :param score_threshold: value to ignore results with score lower than threshold
        :param kwargs: additional parameters for the analyze function
        :return: A dictionary containing the original keys, and a list of results
        (list of list of RecognizerResult) from the various recognizers.
        """

        if not batch:
            raise ValueError(
                "Input not provided. batch should be a dictionary "
                "containing one or more keys with corresponding "
                "lists of strings containing values to analyze"
            )
        if not isinstance(batch, dict):
            raise ValueError(
                "Input parameter batch should be a dict containing "
                "a list of strings per key. "
                "For the analysis of one string, run the analyze function)"
            )

        response = {}
        for key, list_of_texts in batch.items():
            per_text_responses = []
            for text in list_of_texts:
                analyzer_response = self.analyze(
                    text=text,
                    language=language,
                    all_fields=all_fields,
                    entities=entities,
                    score_threshold=score_threshold,
                    **kwargs,
                )
                per_text_responses.append(analyzer_response)
            response[key] = per_text_responses
        return response

    def analyze(
        self,
        text: str,
        language: str,
        all_fields: bool,
        entities: Optional[List[str]] = None,
        correlation_id: Optional[str] = None,
        score_threshold: Optional[float] = None,
        trace: Optional[bool] = False,
    ) -> List[RecognizerResult]:
        """
        analyzes the requested text, searching for the given entities
         in the given language
        :param text: the text to analyze
        :param language: the language of the text
        :param all_fields: True if the analyzer should look for all types of PII,
        False if use only a subset of the recognizers.
        In such case a list of entities should be provided.
        :param entities: List of PII entities that should be looked for in the text.
        If entities=None and all_fields=True then all entities are looked for.
        :param correlation_id: cross call ID for this request
        of the requested language
        :param score_threshold: A minimum value for which
        to return an identified entity
        :param trace: Should tracing of the response occur or not
        :return: an array of the found entities in the text
        """

        if not entities:
            entities = []

        recognizers = self.registry.get_recognizers(
            language=language, entities=entities, all_fields=all_fields
        )

        if all_fields:
            if entities:
                raise ValueError(
                    "Cannot have both all_fields=True "
                    "and a populated list of entities. "
                    "Either have all_fields set to True "
                    "and entities are empty, or all_fields "
                    "is False and entities is populated"
                )
            # Since all_fields=True, list all entities by iterating
            # over all recognizers
            entities = self.__list_entities(recognizers)

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
        results = self._remove_low_scores(results, score_threshold)

        return results

    def _remove_low_scores(
        self, results: List[RecognizerResult], score_threshold: float = None
    ) -> List[RecognizerResult]:
        """
        Removes results for which the confidence is lower than the threshold
        :param results: List of RecognizerResult
        :param score_threshold: float value for minimum possible confidence
        :return: List[RecognizerResult]
        """
        if score_threshold is None:
            score_threshold = self.default_score_threshold

        new_results = [result for result in results if result.score >= score_threshold]
        return new_results

    @staticmethod
    def __list_entities(recognizers: List[EntityRecognizer]):
        """
        Returns a List[str] of unique entity names supported
        by the provided recognizers
        :param recognizers: list of EntityRecognizer
        :return: List[str]
        """
        entities = []
        for recognizer in recognizers:
            entities.extend(recognizer.supported_entities)

        return list(set(entities))
