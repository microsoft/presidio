from abc import ABC, abstractmethod


class EntityRecognizer:

      @abstractmethod
      def load(self):
            pass

      @abstractmethod
      def analyze_text(self, text, entities):
            """
                    This is the core method for analyzing text, assuming field_types are 
                    the subset of the supported field types. 
                    :param text: text to be analyzed
                    :param entities: list of entities to be detected
                    :returns list of TextMatcherResult per found result
            """

            pass
    
      @abstractmethod
      def get_supported_entities(self):
        """
              :returns list of the model's supported fields
        """
      pass

      