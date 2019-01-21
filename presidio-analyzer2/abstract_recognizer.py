from abc import ABC, abstractmethod
import common_pb2
import logging
import os
import tldextract

class AbstractRecognizer(ABC):

      def __init__(self):
        # Set log level
        loglevel = os.environ.get("LOG_LEVEL", "INFO")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)
        logging.getLogger('tldextract').setLevel(loglevel)

        # Caching top level domains
        tldextract.extract("")

      @abstractmethod
      def load_model():
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

            pass
      
      def __sanitize_text(self, text):
        """Replace newline with whitespace to ease spacy analyze process

        Args:
          text: document text
        """

        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        return text

      def analyze_text(self, text, requested_field_types):
          fields_to_analyze = self.__get_fields_to_analyze(requested_field_types)

          if len(fields_to_analyze) > 0:
            return self.__analyze_text_core(self.__sanitize_text(text), fields_to_analyze)
          
          self.logger.info("No supported fields to analyze")
    
      @abstractmethod
      def get_supported_fields(self):
        """
              :returns list of the model's supported fields
        """
      pass
      
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
        res.text = field.text

        # check score
        res.location.start = start
        res.location.end = end
        res.location.length = end - start

        self.logger.debug("field: %s Value: %s Span: '%s:%s' Score: %.2f",
                          res.field, res.text, start, end, res.score)
        return res

      def __get_fields_to_analyze(self, requested_fields):
          supportedFields = self.get_supported_fields() 
          return set(supportedFields).intersection(requested_fields)