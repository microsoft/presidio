import spacy
from analyzer import PatternRecognizer, RecognizerResult

NER_STRENGTH = 0.85
SUPPORTED_ENTITIES = ["DATE_TIME", "NRP", "LOCATION", "PERSON"]

# Import 're2' regex engine if installed, if not- import 'regex'
try:
    import re2 as re
except ImportError:
    import regex as re


class SpacyRecognizer(PatternRecognizer):

    def __init__(self):
        super().__init__(supported_entities=SUPPORTED_ENTITIES, supported_languages=['en'])

    def load(self):
        # Load spaCy sm model
        self.logger.info("Loading NLP model...")
        self.nlp = spacy.load("en_core_web_lg", disable=['parser', 'tagger'])

    def analyze_text(self, text, entities):
        doc = self.nlp(text)
        results = []

        for entity in entities:
            if entity in self.supported_entities:
                for ent in doc.ents:
                    if SpacyRecognizer.__check_label(entity, ent.label_):
                        res = RecognizerResult(ent.start_char, ent.end_char, NER_STRENGTH, entity)
                        res = self.validate_pattern_logic(ent.text, res)
                        if res.score > 0:
                            results.append(res)

        return results

    def validate_pattern_logic(self, text, recognizer_result):
        pattern = r"^[a-zA-Z0-9-_'.() ]+$"
        guid_pattern = r"(\{){0,1}[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}(\}){0,1}"  # noqa: E501
        result = re.match(pattern, text, re.IGNORECASE | re.UNICODE)
        if result is not None:
            if re.match(guid_pattern, text, re.IGNORECASE | re.UNICODE) is not None:
                recognizer_result.score = 0
                return recognizer_result
            return recognizer_result

        recognizer_result.score = 0
        return recognizer_result

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
