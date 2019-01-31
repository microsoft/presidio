class RecognizerResult():
    

    def __init__(self, start, end, score, entity_type):
        """
        TODO: add documentation
        """
        self.start = start
        self.end = end
        self.score = score
        self.entity_type = entity_type