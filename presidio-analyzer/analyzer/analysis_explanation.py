class AnalysisExplanation:

    def __init__(self, recognizer, pattern_name, pattern, original_score):
        """
        """
        self.recognizer = recognizer
        self.pattern_name = pattern_name
        self.pattern = pattern
        self.original_score = original_score
        self.score = original_score

        self.score_context_improvement = 0
        self.supportive_context_word = ''

    def __repr__(self):
        return str(self.__dict__)

    def set_improved_score(self, score):
        self.score = score
        self.score_context_improvement = self.score - self.original_score
    
    def set_supportive_context_word(self, word):
        self.supportive_context_word = word
