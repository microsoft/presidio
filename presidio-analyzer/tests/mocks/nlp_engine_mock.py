from analyzer.nlp_engine import NlpEngine


class MockNlpEngine(NlpEngine):

    def __init__(self, stopwords, nlp_artifacts):
        self.stopwords = stopwords
        self.nlp_artifacts = nlp_artifacts

    def is_stopword(self, word, language):
        return word in self.stopwords

    def process_text(self, text, language):
        return self.nlp_artifacts
