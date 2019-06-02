class RecognizerResult:

    def __init__(self, entity_type, start, end, score,
                 analyze_requestid=None, interpretability_details=None):
        """
        Recognizer Result represents the findings of the detected entity
        of the analyzer in the text.
        :param entity_type: the type of the entity
        :param start: the start location of the detected entity
        :param end: the end location of the detected entity
        :param score: the score of the detection
        """
        self.entity_type = entity_type
        self.start = start
        self.end = end
        self.score = score
        self. analyze_requestid = analyze_requestid
        self.interpretability_details = {}
        if interpretability_details:
            self.interpretability_details = interpretability_details

    def __repr__(self):
        return str(self.__dict__)
