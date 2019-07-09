import json

from . import AnalysisExplanation


class RecognizerResult:

    def __init__(self, entity_type, start, end, score,
                 analysis_explanation: AnalysisExplanation = None):
        """
        Recognizer Result represents the findings of the detected entity
        of the analyzer in the text.
        :param entity_type: the type of the entity
        :param start: the start location of the detected entity
        :param end: the end location of the detected entity
        :param score: the score of the detection
        :param analysis_explanation: contains the explanation of why this
                                     entity was identified
        """
        self.entity_type = entity_type
        self.start = start
        self.end = end
        self.score = score
        self.analysis_explanation = analysis_explanation

    def append_analysis_explenation_text(self, text):
        if self.analysis_explanation:
            self.analysis_explanation.append_textual_explanation_line(text)

    def __repr__(self):
        return str(self.__dict__)

