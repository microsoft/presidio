from entity_recognizer import EntityRecognizer 
from recognizer_result import RecognizerResult

DEFAULT_VERSION = "0.0.1"

class PatternRecognizer(EntityRecognizer):


    def __init__(self, supported_entities, supported_languages, patterns = None, black_list=None, context = None, version = DEFAULT_VERSION):
        """
            TODO: add documentation
        """
        self.super().__init__(supported_entities, supported_languages, version)
        self.patterns = patterns
        self.black_list = black_list
        self.context = context

    def load(self):
        pass


    def analyze_all(self, text, entities):
        results = []

        if self.black_list:
            # Create regex
            # Add to patterns list
        if self.patterns:
            # analyze patterns (move code from pattern_engine)
            # add to results

        results.append(self.analyze_text(text, entities))
        return results



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

    def __calculate_score(self, doc, match_strength, field, start, end):
        """Calculate score of match by context

        Args:
          doc: spacy document to analyze
          match_strength: Base score according to the pattern strength
          field: current field type (pattern)
          start: match start offset
          end: match end offset
        """

        if field.should_check_checksum:
            if field.check_checksum() is not True:
                self.logger.debug('Checksum failed for %s', field.text)
                return 0
            else:
                return 1.0

        score = match_strength

        # Add context similarity
        context = self.__extract_context(doc, start, end)
        context_similarity = self.__calculate_context_similarity(
            context, field)
        if context_similarity >= CONTEXT_SIMILARITY_THRESHOLD:
            score += context_similarity * CONTEXT_SIMILARITY_FACTOR
            score = max(score, MIN_SCORE_WITH_CONTEXT_SIMILARITY)

        return min(score, 1)

        
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

    def __extract_context(self, doc, start, end):
        """Extract context for a specified match

        Args:
          doc: spacy document to analyze
          start: match start offset
          end: match end offset
        """

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
        """Check for specific pattern in text

        Args:
          doc: spacy document to analyze
          results: array containing the created results
          field: current field type (pattern)
        """

        max_matched_strength = -1.0
        for pattern in field.patterns:
            if pattern.strength <= max_matched_strength:
                break
            result_found = False

            match_start_time = datetime.datetime.now()
            matches = re.finditer(
                pattern.regex,
                doc.text,
                flags=re.IGNORECASE | re.DOTALL | re.MULTILINE)
            match_time = datetime.datetime.now() - match_start_time
            self.logger.debug('--- match_time[{}]: {}.{} seconds'.format(
                field.name, match_time.seconds, match_time.microseconds))

            for match in matches:
                start, end = match.span()
                field.text = doc.text[start:end]

                # Skip empty results
                if field.text == '':
                    continue

                # Don't add duplicate
                if len(field.patterns) > 1 and any(
                    ((x.location.start == start) or (x.location.end == end))
                        and ((x.field.name == field.name)) for x in results):
                    continue

                res = self.__create_result(doc, pattern.strength, field, start,
                                           end)

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
        else:
            self.__check_pattern(doc, results, current_field)

        analyze_time = datetime.datetime.now() - analyze_start_time
        self.logger.debug('--- analyze_time[{}]: {}.{} seconds'.format(
            field_type_string_filter, analyze_time.seconds,
            analyze_time.microseconds))