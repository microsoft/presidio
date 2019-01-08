from abc import ABC, abstractmethod

class AbstractMatcher(ABC):

      @abstractmethod
      def load_matcher():
            pass

      @abstractmethod
      def analyze_text(text, requested_field_types):
            """
                    :param text: text to be analyzed
                    :param requested_field_types: list of types to be extracted
                    :returns list of TextMatcherResult per found result
            """

            pass