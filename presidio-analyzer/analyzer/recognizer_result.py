class RecognizerResult:

    def __init__(self, entity_type, start, end, score,
                 request_id=None, result_description=None):
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
        self. request_id = request_id
        self.result_description = {}
        if result_description:
            self.result_description = result_description

    def __repr__(self):
        return str(self.__dict__)
