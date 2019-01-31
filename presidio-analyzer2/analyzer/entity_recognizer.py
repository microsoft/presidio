from abc import ABC, abstractmethod
import common_pb2
import logging
import os
import tldextract

#Change to entity recognizer
class Recognizer(ABC):

    def __init__(self):
        # Set log level
        loglevel = os.environ.get("LOG_LEVEL", "INFO")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)
        logging.getLogger('tldextract').setLevel(loglevel)

        # Caching top level domains
        tldextract.extract("")
        self.loaded = False

    @abstractmethod
    def load_model(self):
        pass

    @abstractmethod
    def __analyze_text_core(self, text, field_types):
        """
                This is the core method for analyzing text, assuming field_types are
                the subset of the supported field types.
                :param text: text to be analyzed
                :param field_types: list of types to be extracted
                :returns list of TextMatcherResult per found result
        """

    @abstractmethod
    def get_supported_entities(self):
        """
              :returns list of the model's supported fields
        """

    @abstractmethod
    def get_patterns(self):
        pass

    @abstractmethod
    def validate_pattern(self, text):
        pass

    @abstractmethod
    def get_context(self):
        pass

    def load_model(self):
        # Load spaCy small model
        self.logger.info("Loading regex model...")
        self.nlp = spacy.load('en_core_web_sm')


    def _Recognizer__analyze_text_core(self, text, field_types):
        results = []

        for field_type_string_filter in field_types:
            self.__analyze_field_type(text, field_type_string_filter, results)

        #results = self.__remove_checksum_duplicates(results)
        results.sort(key=lambda x: x.location.start, reverse=False)

        return results

    def create_result(self, field, start, end, score):
        """Create analyze result

        Args:
          field: current field type (pattern)
          start: match start offset
          end: match end offset
        """

        res = common_pb2.AnalyzeResult()
        res.field.name = field.name
        res.score = score
        # TODO: this should probably needs to be removed.
        #res.text = field.text

        # check score
        res.location.start = start
        res.location.end = end
        res.location.length = end - start

        self.logger.debug("field: %s Value: %s Span: '%s:%s' Score: %.2f",
                          res.field, res.text, start, end, res.score)
        return res

    def analyze_text(self, text, requested_field_types):
        # lazy loading - load only on first use.
        if not self.loaded:
            self.load_model()
            self.loaded = True

        fields_to_analyze = self.__get_fields_to_analyze(requested_field_types)

        if not fields_to_analyze:
            return self.__analyze_text_core(text, fields_to_analyze)

        self.logger.info("No supported fields to analyze")
        return []

    def __get_fields_to_analyze(self, requested_fields):
        supportedFields = self.get_supported_entities()

        return set(supportedFields).intersection(requested_fields)
