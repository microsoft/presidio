import logging
import re

import en_core_web_sm

import common_pb2

from field_types import field_type, types


class Matcher(object):

    def __init__(self):
        self.nlp = en_core_web_sm.load()

    def __calculate_probability__(self, doc, current_field, start):

        probability = 1
        if current_field.should_check_checksum:
            if current_field.check_checksum() is False:
                logging.info("Check sum is 0 for " + current_field.value)
                return 0

       # if hasattr(current_field, 'context') is False or current_field.context is None or len(current_field.context) == 0:
       #    return 0

        base_token = None
        for token in doc:
            if token.idx == start:
                base_token = token
                break
        if base_token is None:
            return 0

        start_index = base_token.i - 5
        propabilities = []

        if start_index < 0:
            start_index = 0
        if len(current_field.context) > 0:
            for token in doc:
                if token.i == base_token.i:
                    break
                if token.i >= start_index:
                    if token.text.lower() in current_field.context:
                        propabilities.append(token)

            if len(propabilities) >= 2:
                probability = 1
            if len(propabilities) == 1:
                probability = probability - 0.2
            if len(propabilities) == 0 and current_field.should_check_checksum is True:
                probability = probability - 0.2
                return probability
            if len(propabilities) == 0:
                probability = 0
        return probability

    def analyze_text(self, text, field_type_filters):
        doc = self.nlp(text)
        results = []
        if field_type_filters is None or field_type_filters == []:
            field_type_filters = types.types_refs.keys()

        for field_type_filter in field_type_filters:
            current_field = types.types_refs[field_type_filter]

            for _, check_type_value in current_field.regexes.items():

                for match in re.finditer(check_type_value, doc.text):

                    start, end = match.span()
                    res = common_pb2.Result()
                    res.fieldType = current_field.name
                    res.value = doc.text[start:end]
                    # don't add duplicate
                    if len(current_field.regexes) > 1 and any(x.location.start == start and x.value == res.value for x in results):
                        break

                    current_field.value = res.value
                    res.location.start = start
                    res.location.end = end
                    res.location.length = end - start
                    res.probability = 1
                    # res.probability = self.__calculate_probability__(
                    #     doc, current_field, start)
                    logging.info(
                        f"FieldType: '{res.fieldType}' Value: '{res.value}' Span: '{start}:{end}' probability: '{res.probability}'")
                    # if res.probability > 0:
                    results.append(res)

        return results
