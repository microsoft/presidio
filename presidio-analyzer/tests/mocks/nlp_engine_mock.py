from analyzer.nlp_engine import NlpEngine


class MockNlpEngine(NlpEngine):

    def __init__(self, stopwords, nlp_artifacts):
        self.stopwords = stopwords
        self.nlp_artifacts = nlp_artifacts
        self.punct_words = []

    def set_punct(self, word):
        self.punct_words.append(word)

    def is_punct(self, word, language):
        return word in self.punct_words

    def is_stopword(self, word, language):
        return word in self.stopwords

    def process_text(self, text, language):
        return self.nlp_artifacts
