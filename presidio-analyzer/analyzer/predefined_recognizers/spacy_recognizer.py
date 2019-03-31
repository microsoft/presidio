import spacy
from analyzer import RecognizerResult, LocalRecognizer

NER_STRENGTH = 0.85
SUPPORTED_ENTITIES = ["DATE_TIME", "NRP", "LOCATION", "PERSON"]


class SpacyRecognizer(LocalRecognizer):

    def __init__(self):
        super().__init__(supported_entities=SUPPORTED_ENTITIES,
                         supported_language='en')

    def load(self):
        # Load spaCy English lg model
        self.logger.info("Loading NLP model...")
        self.nlp = spacy.load("en_core_web_lg", disable=['parser', 'tagger'])

    # pylint: disable=unused-argument
    def analyze(self, text, entities, simplifier=None):
        doc = self.nlp(text)
        results = []

        for entity in entities:
            if entity in self.supported_entities:
                for ent in doc.ents:
                    if SpacyRecognizer.__check_label(entity, ent.label_):
                        results.append(
                            RecognizerResult(entity, ent.start_char,
                                             ent.end_char, NER_STRENGTH))

        return results

    @staticmethod
    def __check_label(entity, label):
        if entity == "LOCATION" and label in ('GPE', 'LOC'):
            return True

        if entity == "PERSON" and label == 'PERSON':
            return True

        if entity == "DATE_TIME" and label in ('DATE', 'TIME'):
            return True

        if entity == "NRP" and label == 'NORP':
            return True

        return False
