from abc import ABC, abstractmethod
import common_pb2
import logging
import os
import tldextract

#Change to entity recognizer
class Recognizer(ABC):

    def __init__(self):
        # Set log level
        loglevel = os.environ.get("LOG_LEVEL", "INFO")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)
        logging.getLogger('tldextract').setLevel(loglevel)

        # Caching top level domains
        tldextract.extract("")
        self.loaded = False

    @abstractmethod
    def load_model(self):
        pass

    @abstractmethod
    def __analyze_text_core(self, text, field_types):
        """
                This is the core method for analyzing text, assuming field_types are
                the subset of the supported field types.
                :param text: text to be analyzed
                :param field_types: list of types to be extracted
                :returns list of TextMatcherResult per found result
        """

    @abstractmethod
    def get_supported_entities(self):
        """
              :returns list of the model's supported fields
        """

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



    def create_result(self, field, start, end, score):
        """Create analyze result

        Args:
          field: current field type (pattern)
          start: match start offset
          end: match end offset
        """

        res = common_pb2.AnalyzeResult()
        res.field.name = field.name
        res.score = score
        # TODO: this should probably needs to be removed.
        #res.text = field.text

        # check score
        res.location.start = start
        res.location.end = end
        res.location.length = end - start

        self.logger.debug("field: %s Value: %s Span: '%s:%s' Score: %.2f",
                          res.field, res.text, start, end, res.score)
        return res

    def analyze_text(self, text, requested_field_types):
        # lazy loading - load only on first use.
        if not self.loaded:
            self.load_model()
            self.loaded = True

        fields_to_analyze = self.__get_fields_to_analyze(requested_field_types)

        if not fields_to_analyze:
            return self.__analyze_text_core(text, fields_to_analyze)

        self.logger.info("No supported fields to analyze")
        return []

    def __get_fields_to_analyze(self, requested_fields):
        supportedFields = self.get_supported_entities()

        return set(supportedFields).intersection(requested_fields)
