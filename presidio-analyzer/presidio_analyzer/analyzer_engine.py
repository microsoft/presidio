import json
import logging
from typing import List, Optional

from presidio_analyzer import (
    RecognizerRegistry,
    RecognizerResult,
    EntityRecognizer,
)
from presidio_analyzer.app_tracer import AppTracer
from presidio_analyzer.context_aware_enhancers import (
    ContextAwareEnhancer,
    LemmaContextAwareEnhancer,
)
from presidio_analyzer.nlp_engine import NlpEngine, NlpEngineProvider, NlpArtifacts

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
    :param context_aware_enhancer: instance of type ContextAwareEnhancer for enhancing
    confidence score based on context words, (LemmaContextAwareEnhancer will be created
    by default if None passed)
    """

    def __init__(
        self,
        registry: RecognizerRegistry = None,
        nlp_engine: NlpEngine = None,
        app_tracer: AppTracer = None,
        log_decision_process: bool = False,
        default_score_threshold: float = 0,
        supported_languages: List[str] = None,
        context_aware_enhancer: Optional[ContextAwareEnhancer] = None,
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
        if not self.nlp_engine.is_loaded():
            self.nlp_engine.load()

        self.registry = registry

        # load all recognizers
        if not registry.recognizers:
            registry.load_predefined_recognizers(
                nlp_engine=self.nlp_engine, languages=self.supported_languages
            )

        self.log_decision_process = log_decision_process
        self.default_score_threshold = default_score_threshold

        if not context_aware_enhancer:
            logger.debug(
                "context aware enhancer not provided, creating default"
                + " lemma based enhancer."
            )
            context_aware_enhancer = LemmaContextAwareEnhancer()

        self.context_aware_enhancer = context_aware_enhancer

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
        context: Optional[List[str]] = None,
        allow_list: Optional[List[str]] = None,
        nlp_artifacts: Optional[NlpArtifacts] = None,
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
        :param context: List of context words to enhance confidence score if matched
        with the recognized entity's recognizer context
        :param allow_list: List of words that the user defines as being allowed to keep
        in the text
        :param nlp_artifacts: precomputed NlpArtifacts
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
        if not nlp_artifacts:
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
                # add recognizer name to recognition metadata inside results
                # if not exists
                self.__add_recognizer_id_if_not_exists(current_results, recognizer)
                results.extend(current_results)

        results = self._enhance_using_context(
            text, results, nlp_artifacts, recognizers, context
        )

        if self.log_decision_process:
            self.app_tracer.trace(
                correlation_id,
                json.dumps([str(result.to_dict()) for result in results]),
            )

        # Remove duplicates or low score results
        results = EntityRecognizer.remove_duplicates(results)
        results = self.__remove_low_scores(results, score_threshold)

        if allow_list:
            results = self._remove_allow_list(results, allow_list, text)

        if not return_decision_process:
            results = self.__remove_decision_process(results)

        return results

    def _enhance_using_context(
        self,
        text: str,
        raw_results: List[RecognizerResult],
        nlp_artifacts: NlpArtifacts,
        recognizers: List[EntityRecognizer],
        context: Optional[List[str]] = None,
    ) -> List[RecognizerResult]:
        """
        Enhance confidence score using context words.

        :param text: The actual text that was analyzed
        :param raw_results: Recognizer results which didn't take
                            context into consideration
        :param nlp_artifacts: The nlp artifacts contains elements
                              such as lemmatized tokens for better
                              accuracy of the context enhancement process
        :param recognizers: the list of recognizers
        :param context: list of context words
        """
        results = []

        for recognizer in recognizers:
            recognizer_results = [
                r
                for r in raw_results
                if r.recognition_metadata[RecognizerResult.RECOGNIZER_IDENTIFIER_KEY]
                == recognizer.id
            ]
            other_recognizer_results = [
                r
                for r in raw_results
                if r.recognition_metadata[RecognizerResult.RECOGNIZER_IDENTIFIER_KEY]
                != recognizer.id
            ]

            # enhance score using context in recognizer level if implemented
            recognizer_results = recognizer.enhance_using_context(
                text=text,
                # each recognizer will get access to all recognizer results
                # to allow related entities contex enhancement
                raw_recognizer_results=recognizer_results,
                other_raw_recognizer_results=other_recognizer_results,
                nlp_artifacts=nlp_artifacts,
                context=context,
            )

            results.extend(recognizer_results)

        # Update results in case surrounding words or external context are relevant to
        # the context words.
        results = self.context_aware_enhancer.enhance_using_context(
            text=text,
            raw_results=results,
            nlp_artifacts=nlp_artifacts,
            recognizers=recognizers,
            context=context,
        )

        return results

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
    def _remove_allow_list(
        results: List[RecognizerResult], allow_list: List[str], text: str
    ) -> List[RecognizerResult]:
        """
        Remove results which are part of the allow list.

        :param results: List of RecognizerResult
        :param allow_list: list of allowed terms
        :param text: the text to analyze
        :return: List[RecognizerResult]
        """
        new_results = []
        for result in results:
            word = text[result.start : result.end]
            # if the word is not specified to be allowed, keep in the PII entities
            if word not in allow_list:
                new_results.append(result)

        return new_results

    @staticmethod
    def __add_recognizer_id_if_not_exists(
        results: List[RecognizerResult], recognizer: EntityRecognizer
    ) -> None:
        """Ensure recognition metadata with recognizer id existence.

        Ensure recognizer result list contains recognizer id inside recognition
        metadata dictionary, and if not create it. recognizer_id is needed
        for context aware enhancement.

        :param results: List of RecognizerResult
        :param recognizer: Entity recognizer
        """
        for result in results:
            if not result.recognition_metadata:
                result.recognition_metadata = dict()
            if (
                RecognizerResult.RECOGNIZER_IDENTIFIER_KEY
                not in result.recognition_metadata
            ):
                result.recognition_metadata[
                    RecognizerResult.RECOGNIZER_IDENTIFIER_KEY
                ] = recognizer.id
            if RecognizerResult.RECOGNIZER_NAME_KEY not in result.recognition_metadata:
                result.recognition_metadata[
                    RecognizerResult.RECOGNIZER_NAME_KEY
                ] = recognizer.name

    @staticmethod
    def __remove_decision_process(
        results: List[RecognizerResult],
    ) -> List[RecognizerResult]:
        """Remove decision process / analysis explanation from response."""

        for result in results:
            result.analysis_explanation = None

        return results
