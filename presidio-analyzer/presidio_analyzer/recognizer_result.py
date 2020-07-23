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

    def to_json(self):
        return str(self.__dict__)

    def __str__(self):
        return "type: {}, " \
               "start: {}, " \
               "end: {}, " \
               "score: {}".format(self.entity_type,
                                  self.start,
                                  self.end,
                                  self.score)

    def __repr__(self):
        return self.__str__()

    def intersects(self, other):
        """
        Checks if self intersects with a different RecognizerResult
        :return: If interesecting, returns the number of
        intersecting characters.
        If not, returns 0
        """

        # if they do not overlap the intersection is 0
        if self.end < other.start or other.end < self.start:
            return 0

        # otherwise the intersection is min(end) - max(start)
        return min(self.end, other.end) - max(self.start, other.start)

    def contained_in(self, other):
        """
        Checks if self is contained in a different RecognizerResult
        :return: true if contained
        """

        return self.start >= other.start and self.end <= other.end
