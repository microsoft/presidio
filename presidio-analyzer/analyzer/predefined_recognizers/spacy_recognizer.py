import spacy
from analyzer import RecognizerResult, LocalRecognizer

NER_STRENGTH = 0.85
SUPPORTED_ENTITIES = ["DATE_TIME", "NRP", "LOCATION", "PERSON"]

# Import 're2' regex engine if installed, if not- import 'regex'
try:
    import re2 as re
except ImportError:
    import regex as re  # noqa: F401


class SpacyRecognizer(LocalRecognizer):

    def __init__(self):
        super().__init__(supported_entities=SUPPORTED_ENTITIES,
                         supported_language='en')

    def load(self):
        # Load spaCy sm model
        self.logger.info("Loading NLP model...")
        self.nlp = spacy.load("en_core_web_lg", disable=['parser', 'tagger'])

    def analyze(self, text, entities):
        doc = self.nlp(text)
        results = []

        for entity in entities:
            if entity in self.supported_entities:
                for ent in doc.ents:
                    if SpacyRecognizer.__check_label(entity, ent.label_):
                        results.append(
                            RecognizerResult(ent.start_char, ent.end_char,
                                             NER_STRENGTH, entity))

        return results

    @staticmethod
    def __check_label(entity, label):
        if entity == "LOCATION" and (label == 'GPE' or label == 'LOC'):
            return True

        if entity == "PERSON" and label == 'PERSON':
            return True

        if entity == "DATE_TIME" and (label == 'DATE' or label == 'TIME'):
            return True

        if entity == "NRP" and label == 'NORP':
            return True

        return False
