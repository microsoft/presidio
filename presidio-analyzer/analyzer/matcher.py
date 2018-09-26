import logging
from concurrent import futures
import re2 as re
import en_core_web_lg
import common_pb2
import template_pb2
import tldextract
from field_types import field_type, field_factory, field_pattern
from field_types.globally import ner

CONTEXT_SIMILARITY_THRESHOLD = 0.65
CONTEXT_SIMILARITY_FACTOR = 0.35
MIN_SCORE_WITH_CONTEXT_SIMILARITY = 0.6
NER_STRENGTH = 0.85
CONTEXT_PREFIX_COUNT = 5
CONTEXT_SUFFIX_COUNT = 0

logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)


class Matcher(object):
    def __init__(self):
        """Constructor
        Load spacy model once
        """

        # Caching top level domains
        logger = logging.getLogger('tldextract')
        logger.setLevel('WARNING')
        tldextract.extract("")

        # Load spaCy lg model
        self.nlp = en_core_web_lg.load(
            disable=['parser', 'tagger', 'textcat', 'tokenizer'])

    def __context_to_keywords(self, context):
        nlp_context = self.nlp(context)

        # Remove punctionation, stop words and take lemma form and remove
        # duplicates
        keywords = list(
            filter(
                lambda k: not self.nlp.vocab[k.text].is_stop and not k.is_punct and k.lemma_ != '-PRON-' and k.lemma_ != 'be',
                nlp_context))
        keywords = list(set(map(lambda k: k.lemma_.lower(), keywords)))

        return keywords

    def __calculate_context_similarity(self, context, field):
        # Context similarity is 1 if there's exact match between a keyword
        # in context
        # and any keyword in field.context

        context_keywords = self.__context_to_keywords(context)

        # TODO: remove after supporting keyphrases (instead of keywords)
        if 'card' in field.context:
            field.context.remove('card')
        if 'number' in field.context:
            field.context.remove('number')

        similarity = 0.0
        for context_keyword in context_keywords:
            if context_keyword in field.context:
                similarity = 1
                break

        return similarity

    def __calculate_probability(self, doc, match_strength, field, start, end):
        if field.should_check_checksum:
            if field.check_checksum() is not True:
                logging.debug('Checksum failed for %s', field.text)
                return 0
            else:
                return 1.0

        # Base probability according to the pattern strength
        probability = match_strength

        # Add context similarity
        context = self.__extract_context(doc, start, end)
        context_similarity = self.__calculate_context_similarity(
            context, field)
        if context_similarity >= CONTEXT_SIMILARITY_THRESHOLD:
            probability += context_similarity * CONTEXT_SIMILARITY_FACTOR
            probability = max(probability, MIN_SCORE_WITH_CONTEXT_SIMILARITY)

        return min(probability, 1)

    def __create_result(self, doc, match_strength, field, start, end):

        res = common_pb2.AnalyzeResult()
        res.field.name = field.name
        res.text = field.text

        # check score
        if isinstance(field, type(ner.Ner())):
            res.probability = NER_STRENGTH
        else:
            res.probability = self.__calculate_probability(
                doc, match_strength, field, start, end)

        res.location.start = start
        res.location.end = end
        res.location.length = end - start

        # logging.debug("field: %s Value: %s Span: '%s:%s' Score: %.2f",
        #             res.field, res.text, start, end, res.probability)
        return res

    def __extract_context(self, doc, start, end):
        prefix = doc.text[0:start].split()
        suffix = doc.text[end + 1:].split()
        context = ''

        context += ' '.join(
            prefix[max(0,
                       len(prefix) - CONTEXT_PREFIX_COUNT):len(prefix)])
        context += ' '
        context += ' '.join(suffix[0:min(CONTEXT_SUFFIX_COUNT, len(suffix))])

        return context

    def __check_pattern(self, doc, results, field):
        max_matched_strength = -1.0
        for pattern in field.patterns:
            if pattern.strength <= max_matched_strength:
                break
            result_found = False
            re.set_fallback_notification(re.FALLBACK_QUIETLY)

            try:
                matches = re.finditer(pattern.regex, doc.text,
                                      re.IGNORECASE | re.UNICODE)

                for match in matches:
                    start, end = match.span()
                    field.text = doc.text[start:end]

                    # Skip empty results
                    if field.text == '':
                        continue

                    # Don't add duplicate
                    if len(field.patterns) > 1 and any(
                        ((x.location.start == start) or
                         (x.location.end == end)) and (
                             (x.field.name == field.name)) for x in results):
                        continue

                    res = self.__create_result(doc, pattern.strength, field,
                                               start, end)

                    if res is None or res.probability == 0:
                        continue

                    # Don't add overlap
                    # if any(x.location.end >= start and x.probability == 1.0
                    #        for x in results):
                    #     continue

                    results.append(res)
                    result_found = True
            except:
                logging.warning("%s failed %s", field.name, pattern.regex)

            if result_found:
                max_matched_strength = pattern.strength

    def __match_ner(self, label, field_type):
        if field_type == "LOCATION" and (label == 'GPE' or label == 'LOC'):
            return True

        if field_type == "PERSON" and label == 'PERSON':
            return True

        if field_type == "DATE_TIME" and (label == 'DATE' or label == 'TIME'):
            return True

        if field_type == "NRP" and label == 'NORP':
            return True

        return False

    def __check_ner(self, doc, results, field):
        for ent in doc.ents:
            if self.__match_ner(ent.label_, field.name) is False:
                continue
            field.text = ent.text

            res = self.__create_result(doc, NER_STRENGTH, field,
                                       ent.start_char, ent.end_char)

            if res is not None:
                results.append(res)

        return results

    def __sanitize_text(self, text):
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        return text

    def __new_payload(self, name, data):
        return type(name, (object, ), data)

    def __analyze_field_type(self, field_type_string_filter, results, doc):
        current_field = field_factory.FieldFactory.create(
            field_type_string_filter)

        if current_field is None:
            return

            # Check for ner field
        if isinstance(current_field, type(ner.Ner())):
            current_field.name = field_type_string_filter
            self.__check_ner(doc, results, current_field)
        else:
            # start_time = datetime.datetime.now()
            self.__check_pattern(doc, results, current_field)
            # test_time = datetime.datetime.now() - start_time
            # logging.debug("%s %f", current_field.name, test_time.microseconds)

    def __is_checksum_result(self, result):
        if result.probability == 1.0:
            result_field = field_factory.FieldFactory.create(result.field.name)
            return result_field.should_check_checksum
        return False

    def __remove_checksum_duplicates(self, results):
        results_with_checksum = list(
            filter(lambda r: self.__is_checksum_result(r), results))

        # Remove matches of the same text, if there's a match with checksum and
        # probability = 1
        filtered_results = []

        for result in results:
            valid_result = True
            if result not in results_with_checksum:
                for result_with_checksum in results_with_checksum:
                    # If result is equal to or substring of a checksum result
                    if (result.text == result_with_checksum.text
                            or (result.text in result_with_checksum.text
                                and result.location.start >=
                                result_with_checksum.location.start
                                and result.location.end <=
                                result_with_checksum.location.end)):
                        valid_result = False
                        break

            if valid_result:
                filtered_results.append(result)

        return filtered_results

    def analyze_text(self, text, field_type_filters):
        """Analyze text.

        Args:
            text: text to analyzer.
            field_type_filters: filters array such as [{"name":PERSON"},{"name": "LOCATION"}]
        """

        results = []
        field_type_string_filters = []

        if field_type_filters is None or not field_type_filters:
            field_type_string_filters = field_factory.types_refs
        else:
            for field_type in field_type_filters:
                field_type_string_filters.append(field_type.name)

        sanitized_text = self.__sanitize_text(text)
        doc = self.nlp(sanitized_text)

        for field_type_string_filter in field_type_string_filters:
            self.__analyze_field_type(field_type_string_filter, results, doc)

        results = self.__remove_checksum_duplicates(results)

        results.sort(key=lambda x: x.location.start, reverse=False)
        return results
