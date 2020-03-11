from presidio_analyzer import RecognizerResult, \
    LocalRecognizer, AnalysisExplanation

NER_STRENGTH = 0.85
SUPPORTED_ENTITIES = ["DATE_TIME", "NRP", "LOCATION", "PERSON"]
SPACY_DEFAULT_EXPLANATION = \
    "Identified as {} by Spacy's Named Entity Recognition"


class SpacyRecognizer(LocalRecognizer):

    def __init__(self):
        super().__init__(supported_entities=SUPPORTED_ENTITIES,
                         supported_language='en')

    def load(self):
        # no need to load anything as the analyze method already receives
        # preprocessed nlp artifacts
        pass

    @staticmethod
    def build_spacy_explanation(recognizer_name, original_score, entity):
        explanation = AnalysisExplanation(
            recognizer=recognizer_name,
            original_score=original_score,
            textual_explanation=SPACY_DEFAULT_EXPLANATION.format(entity))
        return explanation

        # pylint: disable=unused-argument

    def analyze(self, text, entities, nlp_artifacts=None):
        results = []
        if not nlp_artifacts:
            self.logger.warning(
                "Skipping SpaCy, nlp artifacts not provided...")
            return results

        ner_entities = nlp_artifacts.entities

        for entity in entities:
            if entity in self.supported_entities:
                for ent in ner_entities:
                    if SpacyRecognizer.__check_label(entity, ent.label_):
                        explanation = SpacyRecognizer.build_spacy_explanation(
                            self.__class__.__name__,
                            NER_STRENGTH,
                            ent.label_)
                        spacy_result = RecognizerResult(
                            entity, ent.start_char,
                            ent.end_char, NER_STRENGTH, explanation)
                        results.append(spacy_result)

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
