import logging
import regex as re
import en_core_web_sm
import common_pb2
import template_pb2
from field_types import field_type, types
from field_types.globally import ner


class Matcher(object):
    def __init__(self):
        """Constructor
        Load spacy model once
        """

        self.nlp = en_core_web_sm.load(disable=['parser', 'tagger', 'textcat'])

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

        res = common_pb2.AnalyzeResult()
        res.field.name = current_field.name
        res.text = current_field.text

        # Validate checksum
        if current_field.should_check_checksum:
            if current_field.check_checksum() is not True:
                logging.info("Checksum failed for " + current_field.text)
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
            f"field: '{res.field}' Value: '{res.text}' Span: '{start}:{end}' Probability: '{res.probability}'"
        )
        return res

    def __check_pattern(self, doc, results, current_field):
        for _, check_type_value in current_field.regexes.items():

            for match in re.finditer(
                    check_type_value,
                    doc.text,
                    flags=re.IGNORECASE | re.DOTALL | re.MULTILINE,
                    overlapped=False,
                    partial=False,
                    concurrent=True):

                start, end = match.span()
                current_field.text = doc.text[start:end]

                # Skip empty results
                if current_field.text == '':
                    continue

                # Don't add duplicate
                if len(current_field.regexes) > 1 and any(
                        ((x.location.start == start) or (
                            x.location.end == end)) and
                        ((x.text == current_field.text) or (
                            x.field.name == current_field.name))
                        for x in results):
                    continue

                res = self.__create_result(doc, current_field, start, end)
                if res is None or res.probability == 0:
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

    def __check_ner(self, doc, results, current_field):
        for ent in doc.ents:
            if self.__match_ner(ent.label_, current_field.name) is False:
                continue
            current_field.text = ent.text
            res = self.__create_result(doc, current_field, ent.start_char,
                                       ent.end_char)
            res.probability = 0.8

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
        field_type_string_filters = []

        if field_type_filters is None or not field_type_filters:
            field_type_string_filters = types.types_refs.keys()
        else:
            for field_type in field_type_filters:
                field_type_string_filters.append(field_type.name)

        for field_type_string_filter in field_type_string_filters:
            current_field = types.types_refs[field_type_string_filter]

            # Check for ner field
            if isinstance(current_field, type(ner.Ner())):
                current_field.name = field_type_string_filter
                self.__check_ner(doc, results, current_field)
            else:
                self.__check_pattern(doc, results, current_field)

        results.sort(key=lambda x: x.location.start, reverse=False)
        return results
