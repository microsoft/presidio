import datetime

from presidio_analyzer import LocalRecognizer, \
    Pattern, \
    RecognizerResult, \
    EntityRecognizer, \
    AnalysisExplanation

# Import 're2' regex engine if installed, if not- import 'regex'
try:
    import re2 as re
except ImportError:
    import regex as re


class PatternRecognizer(LocalRecognizer):

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
            black_list_pattern = self.__black_list_to_regex(
                black_list)
            self.patterns.append(black_list_pattern)
            self.black_list = black_list
        else:
            self.black_list = []

    def load(self):
        pass

    # pylint: disable=unused-argument,arguments-differ
    def analyze(self, text, entities, nlp_artifacts=None, regex_flags=None):
        results = []

        if self.patterns:
            pattern_result = self.__analyze_patterns(text, regex_flags)

            if pattern_result and self.context:
                # try to improve the results score using the surrounding
                # context words
                enhanced_result = \
                  self.enhance_using_context(
                      text, pattern_result, nlp_artifacts, self.context)
                results.extend(enhanced_result)
            elif pattern_result:
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

    # pylint: disable=unused-argument, no-self-use, assignment-from-none
    def validate_result(self, pattern_text):
        """
        Validates the pattern logic, for example by running
         checksum on a detected pattern.

        :param pattern_text: the text to validated.
        Only the part in text that was detected by the regex engine
        :return: A bool indicating whether the validation was successful.
        """
        return None

    # pylint: disable=unused-argument, no-self-use, assignment-from-none
    def invalidate_result(self, pattern_text):
        """
        Logic to check for result invalidation by running pruning logic.
        For example, each SSN number group should not consist of all the same
        digits.

        :param pattern_text: the text to validated.
        Only the part in text that was detected by the regex engine
        :return: A bool indicating whether the result is invalidated
        """
        return None

    @staticmethod
    def build_regex_explanation(
            recognizer_name,
            pattern_name,
            pattern,
            original_score,
            validation_result):
        explanation = AnalysisExplanation(recognizer=recognizer_name,
                                          original_score=original_score,
                                          pattern_name=pattern_name,
                                          pattern=pattern,
                                          validation_result=validation_result)
        return explanation

    def __analyze_patterns(self, text, flags=None):
        """
        Evaluates all patterns in the provided text, including words in
         the provided blacklist

        :param text: text to analyze
        :param flags: regex flags
        :return: A list of RecognizerResult
        """
        flags = flags if flags else re.DOTALL | re.MULTILINE
        results = []
        for pattern in self.patterns:
            match_start_time = datetime.datetime.now()
            matches = re.finditer(
                pattern.regex,
                text,
                flags=flags)
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

                validation_result = self.validate_result(current_match)
                description = self.build_regex_explanation(
                    self.name,
                    pattern.name,
                    pattern.regex,
                    score,
                    validation_result
                )
                pattern_result = RecognizerResult(
                    self.supported_entities[0],
                    start,
                    end,
                    score,
                    description)

                if validation_result is not None:
                    if validation_result:
                        pattern_result.score = EntityRecognizer.MAX_SCORE
                    else:
                        pattern_result.score = EntityRecognizer.MIN_SCORE

                invalidation_result = self.invalidate_result(current_match)
                if invalidation_result is not None and invalidation_result:
                    pattern_result.score = EntityRecognizer.MIN_SCORE

                if pattern_result.score > EntityRecognizer.MIN_SCORE:
                    results.append(pattern_result)

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
