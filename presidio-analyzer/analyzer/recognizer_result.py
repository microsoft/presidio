class RecognizerResult:

    def __init__(self, start, end, score, entity_type):
        """

        :param start: the start location of the detected entity
        :param end: the end location of the detected entity
        :param score: the score of the detection
        :param entity_type: the type of the entity
        """
        self.start = start
        self.end = end
        self.score = score
        self.entity_type = entity_type
