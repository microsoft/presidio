class AnalysisExplanation:
    """ AnalysisExplanation is a class that holds forensic information that
        helps undestand why PII entities where indentified as such
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, recognizer, pattern_name,
                 pattern, original_score, free_text=None):
        """
        """
        self.recognizer = recognizer
        self.pattern_name = pattern_name
        self.pattern = pattern
        self.original_score = original_score
        self.score = original_score
        self.free_text = free_text
        self.score_context_improvement = 0
        self.supportive_context_word = ''

    def __repr__(self):
        return str(self.__dict__)

    def set_improved_score(self, score):
        """ Updated the score  of the entity and compute the
            improvment fromt the original scoree
        """
        self.score = score
        self.score_context_improvement = self.score - self.original_score

    def set_supportive_context_word(self, word):
        """ Sets the context word which helped increase the score
        """
        self.supportive_context_word = word

    def append_free_text_line(self, text):
        if self.free_text is None:
            self.free_text = text
        else:
            self.free_text = "{}\n{}".format(self.free_text, text)
