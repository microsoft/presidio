import datetime

from analyzer import LocalRecognizer, \
    Pattern, \
    RecognizerResult, \
    EntityRecognizer

# Import 're2' regex engine if installed, if not- import 'regex'
try:
    import re2 as re
except ImportError:
    import regex as re


class PatternRecognizer(LocalRecognizer):

    CONTEXT_SIMILARITY_THRESHOLD = 0.65
    CONTEXT_SIMILARITY_FACTOR = 0.35
    MIN_SCORE_WITH_CONTEXT_SIMILARITY = 0.6
    CONTEXT_PREFIX_COUNT = 5
    CONTEXT_SUFFIX_COUNT = 0

    def __init__(self, supported_entity, name=None,
                 supported_language='en', patterns=None,
                 black_list=None, context=None, version="0.0.1"):
        """
            :param patterns: the list of patterns to detect
            :param black_list: the list of words to detect
            :param context: list of context words
        """
        if not supported_entity:
            raise ValueError(
                "Pattern recognizer should be initialized with entity")

        if not patterns and not black_list:
            raise ValueError(
                "Pattern recognizer should be initialized with patterns"
                " or with black list")

        super().__init__(supported_entities=[supported_entity],
                         supported_language=supported_language,
                         name=name,
                         version=version)
        if patterns is None:
            self.patterns = []
        else:
            self.patterns = patterns
        self.context = context

        if black_list:
            black_list_pattern = PatternRecognizer.__black_list_to_regex(
                black_list)
            self.patterns.append(black_list_pattern)
            self.black_list = black_list
        else:
            self.black_list = []

    def load(self):
        pass

    def analyze(self, text, entities, simplifier=None):
        results = []

        if self.patterns:
            pattern_result = self.__analyze_patterns(text, simplifier)

            if pattern_result:
                results.extend(pattern_result)

        return results

    @staticmethod
    def __black_list_to_regex(black_list):
        """
        Converts a list of word to a matching regex, to be analyzed by the
         regex engine as a part of the analyze logic

        :param black_list: the list of words to detect
        :return:the regex of the words for detection
        """
        regex = r"(?:^|(?<= ))(" + '|'.join(black_list) + r")(?:(?= )|$)"
        return Pattern(name="black_list", regex=regex, score=1.0)

    def __calculate_context_similarity(self,
                                       context_text,
                                       context_list,
                                       simplifier):
        """Context similarity is 1 if there's exact match between a keyword in
           context_text and any keyword in context_list

        :param context_text a string of the prefix and suffix of the found
               match
        :param context_list a list of words considered as context keywords
        :param simplifier makes the context easier to manage.
                          It transforms to singular form, remove punctuation,
                          etc...
        """

        if context_list is None:
            return 0

        context_keywords = self.__context_to_keywords(context_text, simplifier)
        if context_keywords is None:
            return 0

        similarity = 0.0
        for context_keyword in context_keywords:
            if context_keyword in context_list:
                self.logger.info("Found context keyword '%s'", context_keyword)
                similarity = 1
                break

        return similarity

    @staticmethod
    def __context_to_keywords(context, simplifier):
        # if no simplifier is defined, just tokenize the text for best effort
        if simplifier is None:
            return context.split()

        # if a simplifier is defined, use it.
        return simplifier.simplify(context)

    @staticmethod
    def __extract_context(text, start, end):
        """Extract context for a specified match
        Args:
          text: text to analyze
          start: match start offset
          end: match end offset
        """

        prefix = text[0:start].split()
        suffix = text[end + 1:].split()
        context = ''

        context += ' '.join(
            prefix[max(0,
                       len(prefix) -
                       PatternRecognizer.CONTEXT_PREFIX_COUNT):len(prefix)])
        context += ' '
        context += ' '.join(
            suffix[0:min(PatternRecognizer.CONTEXT_SUFFIX_COUNT, len(suffix))])

        return context

    # pylint: disable=unused-argument, no-self-use
    def validate_result(self, pattern_text, pattern_result):
        """
        Validates the pattern logic, for example by running
         checksum on a detected pattern.

        :param pattern_text: the text to validated.
        Only the part in text that was detected by the regex engine
        :param pattern_result: The output of a specific pattern
        detector that needs to be validated
        :return: the updated result of the pattern.
        For example, if a validation logic increased or decreased the score
         that was given by a regex pattern.
        """
        return pattern_result

    def __analyze_patterns(self, text, simplifier):
        """
        Evaluates all patterns in the provided text, including words in
         the provided blacklist

        :param text: text to analyze
        :param simplifier makes the context easier to manage.
                          It transforms to singular form, remove punctuation,
                          etc...
        :return: A list of RecognizerResult
        """
        results = []
        for pattern in self.patterns:
            match_start_time = datetime.datetime.now()
            matches = re.finditer(
                pattern.regex,
                text,
                flags=re.IGNORECASE | re.DOTALL | re.MULTILINE)
            match_time = datetime.datetime.now() - match_start_time
            self.logger.debug('--- match_time[%s]: %s.%s seconds',
                              pattern.name,
                              match_time.seconds,
                              match_time.microseconds)

            for match in matches:
                start, end = match.span()
                current_match = text[start:end]

                # Skip empty results
                if current_match == '':
                    continue

                score = pattern.score
                context_text = self.__extract_context(text, start, end)
                context_similarity = self.__calculate_context_similarity(
                    context_text, self.context, simplifier)
                if context_similarity >= \
                        PatternRecognizer.CONTEXT_SIMILARITY_THRESHOLD:
                    score += \
                        context_similarity * \
                        PatternRecognizer.CONTEXT_SIMILARITY_FACTOR
                    score = max(
                        score,
                        PatternRecognizer.MIN_SCORE_WITH_CONTEXT_SIMILARITY)
                    score = min(
                        score,
                        EntityRecognizer.MAX_SCORE)

                res = RecognizerResult(self.supported_entities[0], start, end,
                                       score)
                res = self.validate_result(current_match, res)
                if res and res.score > EntityRecognizer.MIN_SCORE:
                    results.append(res)

        return results

    def to_dict(self):
        return_dict = super().to_dict()

        return_dict["patterns"] = [pat.to_dict() for pat in self.patterns]
        return_dict["black_list"] = self.black_list
        return_dict["context"] = self.context
        return_dict["supported_entity"] = return_dict["supported_entities"][0]
        del return_dict["supported_entities"]

        return return_dict

    @classmethod
    def from_dict(cls, entity_recognizer_dict):
        patterns = entity_recognizer_dict.get("patterns")
        if patterns:
            patterns_list = [Pattern.from_dict(pat) for pat in patterns]
            entity_recognizer_dict['patterns'] = patterns_list

        return cls(**entity_recognizer_dict)
