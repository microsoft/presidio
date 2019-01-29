import spacy


class PatternEngine:


    def load_model(self):
        # Load spaCy small model
        self.logger.info("Loading regex model...")
        self.nlp = spacy.load('en_core_web_sm')