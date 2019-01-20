import en_core_web_lg
import datetime
import logging
from abstract_recognizer import AbstractRecognizer
from field_types import field_factory
from field_types.globally import ner

NER_STRENGTH = 0.85

class Recognizer(AbstractRecognizer):
    
    def load_model(self): 
        # Load spaCy lg model
        self.logger.info("Loading NLP model...")
        self.nlp = en_core_web_lg.load(disable=['parser', 'tagger'])

    def __check_ner(self, doc, results, field):
        """Check for specific NER in text

        Args:
          doc: spacy document to analyze
          results: array containing the created results
          field: current field type (NER)
        """
        for ent in doc.ents:
            if field.check_label(ent.label_) is False:
                continue
            field.text = ent.text

            if field.validate_result():
                res = super().create_result(field, ent.start_char, ent.end_char, NER_STRENGTH)

                if res is not None:
                    results.append(res)

        self.logger.info(results)
        return results

    def __analyze_field_type(self, doc, field_type_string_filter, results):
        """Analyze specific field type (NER/Pattern)

        Args:
          doc: spacy document to analyze
          field_type_string_filter: field type descriptor
          results: array containing the created results
        """

        current_field = field_factory.FieldFactory.create(
            field_type_string_filter)

        if current_field is None:
            return

        # Check for ner field
        analyze_start_time = datetime.datetime.now()
        if isinstance(current_field, type(ner.Ner())):
            current_field.name = field_type_string_filter
            self.__check_ner(doc, results, current_field)

        analyze_time = datetime.datetime.now() - analyze_start_time
        self.logger.debug('--- analyze_time[{}]: {}.{} seconds'.format(
            field_type_string_filter, analyze_time.seconds,
            analyze_time.microseconds))

    def analyze_text(self, text, requested_field_types):
        doc = self.nlp(text)
        results = []

        for field_type_string_filter in requested_field_types:
            self.__analyze_field_type(doc, field_type_string_filter, results)

        #results = self.__remove_checksum_duplicates(results)
        results.sort(key=lambda x: x.location.start, reverse=False)

        return results