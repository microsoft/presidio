import logging
import regex as re

import en_core_web_sm

from protocol import common_pb2

from field_types import field_type, types
from field_types.globally import ner


class Matcher(object):
    def __init__(self):
        """Constructor
        Load spacy model once
        """

        self.nlp = en_core_web_sm.load()

    def __calculate_probability(self, doc, current_field, start):

        probability = 0.2
        base_token = None
        for token in doc:
            if token.idx == start:
                base_token = token
                break

        if base_token is None:
            return 0

        start_index = base_token.i - 7
        factor = 0.3

        if start_index < 0:
            start_index = 0

        for token in doc:
            if token.i == base_token.i:
                break
            if token.i >= start_index:
                if token.text.lower() in current_field.context:
                    probability = probability + factor
                    if probability >= 1.0:
                        probability = 1.0
                        break

        return probability

    def __create_result(self, doc, current_field, start, end):

        res = common_pb2.Result()
        res.fieldType = current_field.name
        res.value = current_field.value

        # Validate checksum
        if current_field.should_check_checksum:
            if current_field.check_checksum() is False:
                logging.info("Checksum failed for " + current_field.value)
                return None
            else:
                res.probability = 1.0
        else:
            res.probability = self.__calculate_probability(
                doc, current_field, start)

        res.location.start = start
        res.location.end = end
        res.location.length = end - start

        logging.info(
            f"FieldType: '{res.fieldType}' Value: '{res.value}' Span: '{start}:{end}' Probability: '{res.probability}'"
        )
        return res

    def __check_pattern(self, doc, results, current_field):
        for _, check_type_value in current_field.regexes.items():

            for match in re.finditer(
                    check_type_value,
                    doc.text,
                    overlapped=False,
                    partial=False,
                    concurrent=True):

                start, end = match.span()
                current_field.value = doc.text[start:end]

                # Skip empty results
                if current_field.value == '':
                    continue

                res = self.__create_result(doc, current_field, start, end)
                if res is None or res.probability == 0:
                    continue

                # Don't add duplicate
                if len(current_field.regexes) > 1 and any(
                        x.location.start == start and x.value == res.value
                        for x in results):
                    continue

                # Don't add overlap
                if any(x.location.end >= start and x.probability == 1.0
                       for x in results):
                    continue

                results.append(res)

    def __match_ner(self, label, field_type_filter):
        if field_type_filter == "LOCATION" and (label == 'GPE'
                                                or label == 'LOC'):
            return True

        if field_type_filter == "PERSON" and label == 'PERSON':
            return True

        if field_type_filter == "DATE_TIME" and (label == 'DATE'
                                                 or label == 'TIME'):
            return True

        if field_type_filter == "NRP" and label == 'NORP':
            return True

        return False

    def __check_ner(self, doc, results, current_field, field_type_filter):
        for ent in doc.ents:
            if self.__match_ner(ent.label_, field_type_filter) is False:
                continue
            current_field.name = field_type_filter
            current_field.value = ent.text
            res = self.__create_result(doc, current_field, ent.start_char,
                                       ent.end_char)
            res.probability = 0.8
            # Don't add duplicate
            if len(current_field.regexes) > 1 and any(
                    x.location.start == ent.start_char and x.value == res.value
                    for x in results):
                continue

            if res is not None:
                results.append(res)
        return results

    def analyze_text(self, text, field_type_filters):
        """Analyze text.

        Args:
            text: text to analyzer.
            field_type_filters: filters array such as ["PERSON", "LOCATION"]
        """

        doc = self.nlp(text)
        results = []
        if field_type_filters is None or field_type_filters == []:
            field_type_filters = types.types_refs.keys()

        for field_type_filter in field_type_filters:
            current_field = types.types_refs[field_type_filter]

            # Check for ner field
            if isinstance(current_field, type(ner.Ner())):
                current_field.name = field_type_filters
                self.__check_ner(doc, results, current_field,
                                 field_type_filter)
            else:
                self.__check_pattern(doc, results, current_field)

        return results
