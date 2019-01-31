from entity_recognizer import EntityRecognizer
import spacy
import datetime
import logging
import re2 as re
from abc import abstractmethod

CONTEXT_SIMILARITY_THRESHOLD = 0.65
CONTEXT_SIMILARITY_FACTOR = 0.35
MIN_SCORE_WITH_CONTEXT_SIMILARITY = 0.6
NER_STRENGTH = 0.85
CONTEXT_PREFIX_COUNT = 5
CONTEXT_SUFFIX_COUNT = 0


class PatternRecognizer(EntityRecognizer):

    def __init__(self, patterns, context, supported_fields):

        self.patterns = patterns
        self.context = context
        self.supported_fields = supported_fields

    @abstractmethod
    def get_patterns(self):
        pass

    @abstractmethod
    def validate_pattern(self, text):
        pass

    @abstractmethod
    def get_context(self):
        pass

    def load_model(self):
        # Load spaCy small model
        self.logger.info("Loading regex model...")
        self.nlp = spacy.load('en_core_web_sm')
        
    def __check_pattern(self, text, results):
        """Check for specific pattern in text

        Args:
        text: the text to analyze
        results: array containing the created results
        """

        max_matched_strength = -1.0
        for pattern in self.get_patterns():
            if pattern.strength <= max_matched_strength:
                break
            result_found = False

            match_start_time = datetime.datetime.now()
            matches = re.finditer(
                pattern.pattern,
                text,
                flags=re.IGNORECASE | re.DOTALL | re.MULTILINE)
            match_time = datetime.datetime.now() - match_start_time
            self.logger.debug('--- match_time[{}]: {}.{} seconds'.format(
                pattern.name, match_time.seconds, match_time.microseconds))

            for match in matches:
                start, end = match.span()
                text = text[start:end]

                # Skip empty results
                if text == '':
                    continue

                # Don't add duplicate
                if len(self.get_patterns()) > 1 and any(
                    ((x.location.start == start) or (x.location.end == end))
                        and ((x.field.name == pattern.name)) for x in results):
                    continue

                score = self.__calculate_score(text, pattern, start, end)
                res = super().create_result(pattern, start, end, score)

                if res is None or res.score == 0:
                    continue

                # Don't add overlap
                # if any(x.location.end >= start and x.score == 1.0
                #        for x in results):
                #     continue

                results.append(res)
                result_found = True

            if result_found:
                max_matched_strength = pattern.strength

    def _Recognizer__analyze_text_core(self, text, field_types):
        results = []

        for field_type_string_filter in field_types:
            self.__analyze_field_type(text, field_type_string_filter, results)

        #results = self.__remove_checksum_duplicates(results)
        results.sort(key=lambda x: x.location.start, reverse=False)

        return results

    def __analyze_field_type(self, text, field_type_string_filter, results):
        """Analyze specific field type (NER/Pattern)

        Args:
          text: the text to analyze
          field_type_string_filter: field type descriptor
          results: array containing the created results
        """

        # current_field = field_factory.FieldFactory.create(field_type_string_filter)

        # if current_field is None:
        #     return

        analyze_start_time = datetime.datetime.now()
        self.__check_pattern(text, results)

        analyze_time = datetime.datetime.now() - analyze_start_time
        self.logger.debug('--- analyze_pattern_time[{}]: {}.{} seconds'.format(
            field_type_string_filter, analyze_time.seconds,
            analyze_time.microseconds))

    @staticmethod
    def __extract_context(text, start, end):
        """Extract context for a specified match

        Args:
          text: the text to analyze
          start: match start offset
          end: match end offset
        """

        prefix = text[0:start].split()
        suffix = text[end + 1:].split()
        context = ''

        context += ' '.join(
            prefix[max(0,
                       len(prefix) - CONTEXT_PREFIX_COUNT):len(prefix)])
        context += ' '
        context += ' '.join(suffix[0:min(CONTEXT_SUFFIX_COUNT, len(suffix))])

        return context


    def __calculate_score(self, text, pattern, start, end):
        """Calculate score of match by context

        Args:
          text: the text to analyze
          field: current field type (pattern)
          start: match start offset
          end: match end offset
        """

        if pattern.validate_pattern() is not True:
            self.logger.debug('Checksum failed for %s', text)
            return 0

        score = pattern.strength

        # Add context similarity
        context = PatternRecognizer.__extract_context(text, start, end)
        context_similarity = self.__calculate_context_similarity(
            context, pattern)
        if context_similarity >= CONTEXT_SIMILARITY_THRESHOLD:
            score += context_similarity * CONTEXT_SIMILARITY_FACTOR
            score = max(score, MIN_SCORE_WITH_CONTEXT_SIMILARITY)

        return min(score, 1)

    def __calculate_context_similarity(self, context, field):
        """Context similarity is 1 if there's exact match between a keyword in
           context and any keyword in field.context

        Args:
          context: words prefix of specified pattern
          field: current field type (pattern)
        """

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

    def __context_to_keywords(self, context):
        """Convert context text to relevant keywords

        Args:
           context: words prefix of specified pattern
        """

        nlp_context = self.nlp(context)

        # Remove punctuation, stop words and take lemma form and remove
        # duplicates
        keywords = list(
            filter(
                lambda k: not self.nlp.vocab[k.text].is_stop and not k.is_punct and k.lemma_ != '-PRON-' and k.lemma_ != 'be',  # noqa: E501
                nlp_context))
        keywords = list(set(map(lambda k: k.lemma_.lower(), keywords)))

        return keywords
