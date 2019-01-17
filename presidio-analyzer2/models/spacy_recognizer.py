import en_core_web_lg

class SpacyRecognizer(AbstractRecognizer) {
    
    def load_model(self): 
        # Load spaCy lg model
        self.logger.info("Loading NLP model...")
        self.nlp = en_core_web_lg.load(disable=['parser', 'tagger'])

    def analyze_text(self, text, requested_field_types):
        pass
}