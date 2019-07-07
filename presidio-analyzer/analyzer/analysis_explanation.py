class AnalysisExplanation:
    """ AnalysisExplanation is a class that holds tracing information
     to explain why PII entities where indentified as such
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, recognizer, pattern_name,
                 pattern, original_score, validation_result,
                 textual_explanation=None):
        """
        """
        self.recognizer = recognizer
        self.pattern_name = pattern_name
        self.pattern = pattern
        self.original_score = original_score
        self.score = original_score
        self.textual_explanation = textual_explanation
        self.score_context_improvement = 0
        self.supportive_context_word = ''
        self.validation_result = validation_result

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

    def append_textual_explanation_line(self, text):
        """Appends a new line to textual_explanation field"""
        if self.textual_explanation is None:
            self.textual_explanation = text
        else:
            self.textual_explanation = "{}\n{}".format(
                self.textual_explanation, text)
