import spacy
from pattern_recognizer import PatternRecognizer

NER_STRENGTH = 0.85

class SpacyRecognizer(PatternRecognizer):

    def __init__(self):
        super().__init__()

    def load(self):
        # Load spaCy sm model
        self.logger.info("Loading NLP model...")
        self.nlp = spacy.load("en_core_web_lg", disable=['parser', 'tagger'])

    def __check_ner(self, doc, results, entity):
        """
        Check for specific NER in text

        Args:
        doc: spacy document to analyze
        results: array containing the created results
        entity: current entity type (NER)
        """
        for ent in doc.ents:
            if SpacyRecognizer.check_label(entity, ent.label_) is False:
                continue
            entity.text = ent.text

            if entity.validate_result():
                res = super().create_result(entity, ent.start_char, ent.end_char, NER_STRENGTH)

                if res is not None:
                    results.append(res)

        
        return results

    def __analyze_field_type(self, doc, entity, results):
        """Analyze specific field type (NER)

        Args:
          doc: spacy document to analyze
          entity: the entity type
          results: array containing the created results
        """

        # Not sure if this code is needed.. maybe the following is enough
        self.__check_ner(doc, results, entity)
        # # Check for ner field
        # analyze_start_time = datetime.datetime.now()
        # if isinstance(current_field, type(ner.Ner())):
        #     current_field.name = field_type_string_filter
        #     self.__check_ner(doc, results, current_field)

        # analyze_time = datetime.datetime.now() - analyze_start_time
        # self.logger.debug('--- analyze_time[{}]: {}.{} seconds'.format(
        #     field_type_string_filter, analyze_time.seconds,
        #     analyze_time.microseconds))

    def analyze_text_core(self, text, entities):
        doc = self.nlp(text)
        results = []

        for entity in entities:
            self.__analyze_field_type(doc, entity, results)

        results.sort(key=lambda x: x.location.start, reverse=False)

        return results

    def get_supported_entities(self):
        return ["DATE_TIME", "NRP", "LOCATION", "PERSON"]

    @staticmethod
    def check_label(entity, label):
        if entity == "LOCATION" and (label == 'GPE' or label == 'LOC'):
            return True

        if entity == "PERSON" and label == 'PERSON':
            return True

        if entity == "DATE_TIME" and (label == 'DATE' or label == 'TIME'):
            return True

        if entity == "NRP" and label == 'NORP':
            return True

        return False
