from analyzer.nlp_engine import NlpEngine


class MockNlpEngine(NlpEngine):

    def __init__(self, stopwords, punct_words, nlp_artifacts):
        self.stopwords = stopwords
        self.punct_words = punct_words
        self.nlp_artifacts = nlp_artifacts

    def is_stopword(self, word, language):
        return word in self.stopwords

    def is_punct(self, word, language):
        return word in self.punct_words

    def process_text(self, text, language):
        return self.nlp_artifacts
