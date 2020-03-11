class AnalysisExplanation:

    # pylint: disable=too-many-instance-attributes
    def __init__(self, recognizer, original_score, pattern_name=None,
                 pattern=None, validation_result=None,
                 textual_explanation=None):
        """
        AnalysisExplanation is a class that holds tracing information
        to explain why PII entities where indentified as such
        :param recognizer: name of recognizer that made the decision
        :param original_score: recognizer's confidence in result
        :param pattern_name: name of pattern
                (if decision was made by a PatternRecognizer)
        :param pattern: regex pattern that was applied (if PatternRecognizer)
        :param validation_result: result of a validation (e.g. checksum)
        :param textual_explanation: Free text for describing
                a decision of a logic or model
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
