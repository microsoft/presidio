from presidio_analyzer.nlp_engine import NlpEngine, NlpArtifacts


class MockNlpEngine(NlpEngine):

    def __init__(self, stopwords=[], punct_words=[], nlp_artifacts=None):
        self.stopwords = stopwords
        self.punct_words = punct_words
        if nlp_artifacts is None:
            self.nlp_artifacts = NlpArtifacts([], [], [], [], None, "en")
        else:
            self.nlp_artifacts = nlp_artifacts

    def is_stopword(self, word, language):
        return word in self.stopwords

    def is_punct(self, word, language):
        return word in self.punct_words

    def process_text(self, text, language):
        return self.nlp_artifacts
