from analyzer.nlp_engine import NlpEngine


class MockNlpEngine(NlpEngine):

    def __init__(self, stopwords, nlpArtifacts):
        self.stopwords = stopwords
        self.nlpArtifacts = nlpArtifacts

    def is_stopword(self, word, language):
        return word in self.stopwords

    def process_text(self, text, language):
        return self.nlpArtifacts
