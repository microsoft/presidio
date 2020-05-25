import json
import uuid

from presidio_analyzer import PresidioLogger, RecognizerRegistry
from presidio_analyzer.app_tracer import AppTracer
from presidio_analyzer.protobuf_models import analyze_pb2, analyze_pb2_grpc, common_pb2
from presidio_analyzer.recognizer_registry import RecognizerStoreApi
from presidio_analyzer.nlp_engine import NLP_ENGINES


logger = PresidioLogger("presidio")


# pylint: disable=no-member
class AnalyzerEngine(analyze_pb2_grpc.AnalyzeServiceServicer):

    def __init__(self, registry=None, nlp_engine=None,
                 app_tracer=None, enable_trace_pii=False,
                 default_score_threshold=None, use_recognizer_store=False,
                 default_language="en"):
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
        :param use_recognizer_store Whether to call the
        Presidio Recognizer Store on every request to gather
        responses from custom recognizers as well
        (only applicable for the full Presidio service)
        """
        if not nlp_engine:
            logger.info("nlp_engine not provided. Creating new "
                        "SpacyNlpEngine instance")
            nlp_engine = NLP_ENGINES["spacy"]()
        if not registry:
            logger.info("Recognizer registry not provided. "
                        "Creating default RecognizerRegistry instance")
            if use_recognizer_store:
                recognizer_store_api = RecognizerStoreApi()
            else:
                recognizer_store_api = None
            registry = RecognizerRegistry(recognizer_store_api=recognizer_store_api)
        if not app_tracer:
            app_tracer = AppTracer()

        # load nlp module
        self.nlp_engine = nlp_engine
        # prepare registry
        self.registry = registry
        # load all recognizers
        if not registry.recognizers:
            registry.load_predefined_recognizers()

        self.app_tracer = app_tracer
        self.enable_trace_pii = enable_trace_pii

        self.default_score_threshold = default_score_threshold \
            if default_score_threshold \
            else 0.0

        self.default_language = default_language

    # pylint: disable=unused-argument
    def GetAllRecognizers(self, request, context):
        """
        GRPC entry point to Presidio-Analyzer Get all Recognizers method
        :param request: Presidio Analyzer resuest of type RecognizersAllRequest
        :param context:
        :return: List of [Recognizer] as a RecognizersAllResponse
        """
        logger.info("Starting Analyzer's Get All Recognizers")
        language = request.language
        if not language:
            language = self.default_langauge
        results = []
        recognizers = self.registry.get_recognizers(
            language=language,
            all_fields=True)
        for recognizer in recognizers:
            results.append(
                AnalyzerEngine.__convert_recognizer_to_proto(recognizer))
        return results

    # pylint: disable=unused-argument
    def Apply(self, request, context):
        """
        GRPC entry point to Presidio-Analyzer Apply method
        :param request: Presidio Analyzer resuest of type AnalyzeRequest
        :param context:
        :return: List of [AnalyzeResult]
        """
        logger.info("Starting Analyzer's Apply")

        entities = self.__convert_fields_to_entities(
            request.analyzeTemplate.fields)
        language = self.get_language_from_request(request)

        threshold = request.analyzeTemplate.resultsScoreThreshold
        all_fields = request.analyzeTemplate.allFields

        # correlation is used to group all traces related to on request

        correlation_id = str(uuid.uuid4())
        logger.info(f"""text: {request.text}\n
                        entities: {entities}\n
                        language: {language}\n
                        all_fields: {all_fields}""")
        results = self.analyze(correlation_id=correlation_id,
                               text=request.text,
                               entities=entities,
                               language=language,
                               all_fields=all_fields,
                               score_threshold=threshold,
                               trace=True)

        # Create Analyze Response Object
        response = analyze_pb2.AnalyzeResponse()

        response.requestId = correlation_id
        # pylint: disable=no-member
        response.analyzeResults.extend(
            self.__convert_results_to_proto(results))

        logger.info("Found %d results", len(results))
        return response

    @staticmethod
    def __remove_duplicates(results):
        """
        Removes each result which has a span contained in a
        result's span with a higher score
        :param results: List[RecognizerResult]
        :return: List[RecognizerResult]
        """
        # bug# 597: Analyzer remove duplicates doesn't handle all cases of one
        # result as a substring of the other
        results = sorted(results,
                         key=lambda x: (-x.score, x.start, x.end - x.start))
        filtered_results = []

        for result in results:
            if result.score == 0:
                continue

            valid_result = True
            if result not in filtered_results:
                for filtered in filtered_results:
                    # If result is equal to or substring of
                    # one of the other results

                    if result.contained_in(filtered) and \
                       result.entity_type == filtered.entity_type:
                        valid_result = False
                        break

            if valid_result:
                filtered_results.append(result)

        return filtered_results

    def __remove_low_scores(self, results, score_threshold=None):
        """
        Removes results for which the confidence is lower than the threshold
        :param results: List of RecognizerResult
        :param score_threshold: float value for minimum possible confidence
        :return: List[RecognizerResult]
        """
        if score_threshold is None:
            score_threshold = self.default_score_threshold

        new_results = []
        for result in results:
            if result.score >= score_threshold:
                new_results.append(result)

        return new_results

    def get_language_from_request(self, request):
        language = request.analyzeTemplate.language
        if not language:
            language = self.default_language
        return language

    def analyze(self, text, language, all_fields, entities=None, correlation_id=None,
                score_threshold=None, trace=False):
        """
        analyzes the requested text, searching for the given entities
         in the given language
        :param text: the text to analyze
        :param entities: the text to search
        :param language: the language of the text
        :param all_fields: a Flag to return all fields
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
            language=language,
            entities=entities,
            all_fields=all_fields)

        if all_fields:
            if entities:
                raise ValueError("Cannot have both all_fields=True "
                                 "and a populated list of entities. "
                                 "Either have all_fields set to True "
                                 "and entities are empty, or all_fields "
                                 "is False and entities is populated")
            # Since all_fields=True, list all entities by iterating
            # over all recognizers
            entities = self.__list_entities(recognizers)

        # run the nlp pipeline over the given text, store the results in
        # a NlpArtifacts instance
        nlp_artifacts = self.nlp_engine.process_text(text, language)

        if self.enable_trace_pii and trace:
            self.app_tracer.trace(correlation_id, "nlp artifacts:"
                                  + nlp_artifacts.to_json())

        results = []
        for recognizer in recognizers:
            # Lazy loading of the relevant recognizers
            if not recognizer.is_loaded:
                recognizer.load()
                recognizer.is_loaded = True

            # analyze using the current recognizer and append the results
            current_results = recognizer.analyze(text=text,
                                                 entities=entities,
                                                 nlp_artifacts=nlp_artifacts)
            if current_results:
                results.extend(current_results)

        if trace:
            self.app_tracer.trace(correlation_id, json.dumps(
                [result.to_json() for result in results]))

        # Remove duplicates or low score results
        results = self.__remove_duplicates(results)
        results = self.__remove_low_scores(results, score_threshold)

        return results

    @staticmethod
    def __list_entities(recognizers):
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

    @staticmethod
    def __convert_fields_to_entities(fields):
        """
        Converts the Field object to the name of the entity
        :param fields: List of Fields in AnalyzeTemplate
        :return: List[str] with field names
        """
        return [field.name for field in fields]

    @staticmethod
    def __convert_results_to_proto(results):
        """
        Converts a List[RecognizerResult] to List[AnalyzeResult]
        :param results: List[RecognizerResult]
        :return: List[AnalyzeResult]
        """
        proto_results = []
        for result in results:
            res = common_pb2.AnalyzeResult()
            # pylint: disable=no-member
            res.field.name = result.entity_type
            res.score = result.score
            # pylint: disable=no-member
            res.location.start = result.start
            res.location.end = result.end
            res.location.length = result.end - result.start
            proto_results.append(res)

        return proto_results

    @staticmethod
    def __convert_recognizer_to_proto(result):
        """
        Converts a List of recognizers to a list of protobuf List[Recognizer]
        :param results: List[recognizer]
        :return: List[Recognizer]
        """
        res = analyze_pb2.Recognizer()
        res.name = result.name
        for entity in result.supported_entities:
            # pylint: disable=no-member
            res.entities.append(entity)
        res.language = result.supported_language
        return res
