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
      def analyze_text(text, requested_field_types):
            """
                    :param text: text to be analyzed
                    :param requested_field_types: list of types to be extracted
                    :returns list of TextMatcherResult per found result
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